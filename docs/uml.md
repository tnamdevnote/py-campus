# PyCampus Classroom: UML class diagram (Python version)

These are the server-side classes for the planned FastAPI version (see [architecture.md](architecture.md)). The diagrams are split into the domain model and the message protocol so each one stays readable.

## 1. Domain model

```mermaid
classDiagram
  direction LR

  class Position {
    <<value object, frozen dataclass>>
    +x: float
    +z: float
    +ry: float
    +clamped(limit: float) Position
    +distance_to(other: Position) float
  }

  class Entity {
    <<abstract>>
    +id: str
    +position: Position
    +move_to(pos: Position)* None
    +to_dict()* dict
  }

  class Player {
    <<abstract>>
    +name: str
    +color: str
    +seat: Seat | None
    +hand_raised: bool
    +sit(seat: Seat) None
    +stand() None
    +toggle_hand() None
    +can_spotlight()* bool
    +role()* str
  }

  class Student {
    +pane: CodePane
    +can_spotlight() bool
    +role() str
  }

  class Professor {
    +can_spotlight() bool
    +role() str
    +post_problem(board: Whiteboard, text: str) None
    +spotlight(board: Whiteboard, student: Student) None
  }

  class Room {
    <<abstract>>
    +MAX_PLAYERS: int = 10
    #players: dict[str, Player]
    +join(player: Player)* None
    +leave(player_id: str)* None
    +broadcast(msg: Message, exclude: str | None) None
    +tick(dt: float) None
    +is_full() bool
  }

  class Classroom {
    -professor_id: str | None
    +seats: list[Seat]
    +whiteboard: Whiteboard
    +join(player: Player) None
    +leave(player_id: str) None
    +professor_slot_open() bool
    +free_seat_near(pos: Position) Seat | None
    +snapshot() dict
  }

  class Seat {
    +index: int
    +position: Position
    +occupant_id: str | None
    +occupy(player: Player) None
    +release() None
    +is_free() bool
  }

  class Whiteboard {
    +problem: str
    +spotlight_id: str | None
    +set_problem(text: str) None
    +set_spotlight(student_id: str | None) None
    +clear_spotlight() None
  }

  class CodePane {
    +owner_id: str
    +text: str
    +MAX_CHARS: int = 10000
    +updated_at: float
    +update(text: str) None
  }

  Entity <|-- Player
  Player <|-- Student
  Player <|-- Professor
  Room <|-- Classroom
  Entity *-- Position : has
  Seat *-- Position : has
  Classroom "1" *-- "many" Seat : seats
  Classroom "1" *-- "1" Whiteboard : board
  Classroom "1" o-- "0..10" Player : players
  Classroom "1" o-- "0..1" Professor : professor slot
  Student "1" *-- "1" CodePane : owns
  Player "0..1" --> "0..1" Seat : sits in
  Whiteboard ..> Student : spotlights
```

**OOP ideas shown here**

- **Abstraction:** `Entity`, `Player` and `Room` are abstract base classes (`abc.ABC`). They can't be created directly.
- **Inheritance and polymorphism:** `Student` and `Professor` override `can_spotlight()` and `role()`. The handler calls `player.can_spotlight()` without checking the type.
- **Encapsulation:** `Classroom` keeps `professor_id` private and exposes `professor_slot_open()`. `CodePane.update()` enforces the size limit itself.
- **Composition vs aggregation:** a `Classroom` owns its seats and whiteboard (they're created and destroyed with it), but only references players, who come and go.
- **Value object:** `Position` is a frozen dataclass, so moving creates a new `Position` instead of changing one in place.

## 2. Message protocol

```mermaid
classDiagram
  direction TB

  class Message {
    <<abstract>>
    +type: ClassVar[str]
    +sender_id: str
    +to_json() str
    +from_json(raw: str)$ Message
    +apply(room: Classroom, sender: Player)* None
  }

  class MessageRegistry {
    <<singleton>>
    -types: dict[str, type[Message]]
    +register(cls)$ type[Message]
    +lookup(type_name: str)$ type[Message]
  }

  class Join {
    +name: str
    +role: str
  }
  class Move {
    +position: Position
  }
  class Chat {
    +text: str
  }
  class Sit {
    +seat_index: int | None
  }
  class RaiseHand {
    +raised: bool
  }
  class CodeUpdate {
    +text: str
  }
  class PostProblem {
    +text: str
  }
  class Spotlight {
    +student_id: str | None
  }
  class RoleChange {
    +role: str
  }

  Message <|-- Join
  Message <|-- Move
  Message <|-- Chat
  Message <|-- Sit
  Message <|-- RaiseHand
  Message <|-- CodeUpdate
  Message <|-- PostProblem
  Message <|-- Spotlight
  Message <|-- RoleChange
  MessageRegistry ..> Message : creates by type

  class MessageHandler {
    -room: Classroom
    -filters: list[ChatFilter]
    +handle(raw: str, sender: Player) None
    -authorize(msg: Message, sender: Player) bool
  }

  class ChatFilter {
    <<interface>>
    +filter(text: str) str | None
  }
  class LengthFilter {
    +max_len: int = 200
  }
  class WordFilter {
    +blocked: set[str]
  }

  ChatFilter <|.. LengthFilter
  ChatFilter <|.. WordFilter
  MessageHandler --> MessageRegistry : parses with
  MessageHandler --> ChatFilter : applies 0..*
  MessageHandler --> Classroom : updates
```

**How it fits together**

1. `MessageHandler.handle()` reads `type` from the JSON, asks `MessageRegistry.lookup()` for the class, and builds it with `from_json()`.
2. `authorize()` rejects messages the sender isn't allowed to send. For example, `Spotlight` and `PostProblem` need `sender.can_spotlight()`.
3. `Chat` text passes through each `ChatFilter` in order. A filter can shorten the text, or return `None` to drop the message.
4. `msg.apply(room, sender)` changes the state, and the room broadcasts the result with `to_json()`.

Each subclass registers itself with a decorator (`@MessageRegistry.register`). To add a new message type, you write one class and change nothing else, which shows the **open/closed principle**.

## 3. Lifecycle of the professor slot

```mermaid
stateDiagram-v2
  [*] --> Open
  Open --> Taken : join(role="professor")
  Taken --> Taken : join(role="professor") refused
  Taken --> Open : professor leaves / whiteboard.clear_spotlight()
```
