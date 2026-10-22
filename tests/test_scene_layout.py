"""Regression checks for contrast layering and measured text layout."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('layout', Path(__file__).parents[1]/'scripts/check_scene_layout.py')
layout = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(layout)


def text(**overrides):
    return dict(type='text', x=50, y=50, w=200, h=40, fontSize=20, text='Test', **overrides)


def scene(*elements):
    return dict(width=1280, height=720, slides=[dict(frame=False, elements=list(elements))])


def measured(content, size, bold):
    return len(content)*size*.5


class SceneLayoutTests(unittest.TestCase):
    def test_wrapping_height_is_measured(self):
        element = text()
        element.update(text='abcdefghijkl', w=40, h=40)
        report = layout.audit(scene(element), measured)
        self.assertTrue(any('text height' in e for e in report['errors']))

    def test_single_wide_glyph_is_detected(self):
        element = text()
        element.update(text='字', w=4)
        self.assertTrue(any('glyph' in e for e in layout.audit(scene(element), measured)['errors']))

    def test_contrast_uses_latest_underlying_rectangle(self):
        dark = dict(type='rect', x=0, y=0, w=400, h=200, fill='000000')
        white = text(color='FFFFFF')
        report = layout.audit(scene(dark, white), measured)
        self.assertFalse(report['warnings'])
        report = layout.audit(scene(dark, text(color='111111')), measured)
        self.assertTrue(any('low contrast' in w for w in report['warnings']))

    def test_line_does_not_override_background(self):
        line = dict(type='line', points=[[0, 60], [400, 60]], stroke='000000')
        self.assertFalse(layout.audit(scene(line, text()), measured)['warnings'])

    def test_partial_background_is_unverified(self):
        half = dict(type='rect', x=50, y=50, w=10, h=100, fill='000000')
        self.assertTrue(any('contrast unverified' in w for w in layout.audit(scene(half, text()), measured)['warnings']))

    def test_alignment_avoids_empty_box_false_overlap(self):
        first, second = text(), text()
        first.update(w=300)
        second.update(x=200, w=150, align='right')
        self.assertFalse(any('overlaps' in w for w in layout.audit(scene(first, second), measured)['warnings']))
        second.update(x=55, align='left')
        self.assertTrue(any('overlaps' in w for w in layout.audit(scene(first, second), measured)['warnings']))

    def test_missing_font_and_canvas_are_explicit(self):
        element = text()
        element.update(x=1250)
        report = layout.audit(scene(element))
        self.assertTrue(report['errors'])
        self.assertFalse(report['textFitMeasured'])
        self.assertIn('unverified', report['warnings'][0])


if __name__ == '__main__':
    unittest.main()
