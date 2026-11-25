import math

import landmarks as lm


def _by_name(name):
    return next(l for l in lm.LANDMARKS if l.name == name)


def test_origin_projects_to_zero():
    assert lm.latlon_to_xz(*lm.ORIGIN) == (0.0, 0.0)


def test_projection_scale():
    # 0.001 deg latitude is ~111 m.
    _, z = lm.latlon_to_xz(lm.ORIGIN[0] + 0.001, lm.ORIGIN[1])
    assert math.isclose(z, 111.2, abs_tol=0.5)


def test_landmark_layout_matches_real_world():
    tower = lm.latlon_to_xz(*(_by_name("UT Tower").lat, _by_name("UT Tower").lon))
    coop = _by_name("University Co-op")
    mall = _by_name("West Mall entrance")
    coop_x, _ = lm.latlon_to_xz(coop.lat, coop.lon)
    mall_x, _ = lm.latlon_to_xz(mall.lat, mall.lon)
    guad_x, _ = lm.latlon_to_xz(*lm.GUADALUPE_NORTH)
    # Co-op west of Guadalupe, West Mall entrance east of it, Tower further east.
    assert coop_x < guad_x < mall_x < tower[0]
    # Tower is a background landmark: a couple hundred metres from the Drag.
    assert 150 < tower[0] - guad_x < 350


def test_tower_height():
    top = max(p.offset[1] + p.size[1] for p in _by_name("UT Tower").parts)
    assert math.isclose(top, 94, abs_tol=2)  # 307 ft


def test_sidewalks_flank_the_road():
    slabs = lm.sidewalks(lm.latlon_to_xz)
    west, east = slabs[0], slabs[1]
    gap = east.x - west.x
    assert math.isclose(gap, lm.ROAD_WIDTH + lm.SIDEWALK_WIDTH, abs_tol=0.5)
    assert all(s.length > 0 for s in slabs)
    # Sidewalks are clear of the Co-op and West Mall entrance footprints' centres.
    assert west.x < 0 < east.x
