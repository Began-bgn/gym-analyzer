import pytest
from werkzeug.datastructures import MultiDict

from app import parse_workout


def form(*pairs):
    return MultiDict([("workout_date", "2026-10-26"), *pairs])


def test_any_number_of_sets_and_exercises():
    f = form(("exercise_0", "1"), *[("reps_0", "5"), ("weight_0", "100")] * 8,
             ("exercise_3", "2"), ("reps_3", "10"), ("weight_3", "40"))
    _, _, sets = parse_workout(f, {1, 2})
    assert len(sets) == 9
    assert sets[7] == (1, 8, 5, 100.0)  # 8th set of exercise 1
    assert sets[8] == (2, 1, 10, 40.0)  # numbering restarts per exercise


def test_same_exercise_in_two_blocks_keeps_counting():
    f = form(("exercise_0", "1"), ("reps_0", "5"), ("weight_0", "100"),
             ("exercise_1", "1"), ("reps_1", "3"), ("weight_1", "110"))
    _, _, sets = parse_workout(f, {1})
    assert [s[1] for s in sets] == [1, 2]


@pytest.mark.parametrize("pairs", [
    [],                                                               # nothing
    [("exercise_0", ""), ("reps_0", "5"), ("weight_0", "100")],       # no exercise
    [("exercise_0", "9"), ("reps_0", "5"), ("weight_0", "100")],      # unknown id
    [("exercise_0", "1"), ("reps_0", "0"), ("weight_0", "100")],      # zero reps
    [("exercise_0", "1"), ("reps_0", "5"), ("weight_0", "-1")],       # negative weight
    [("exercise_0", "1"), ("reps_0", ""), ("weight_0", "100")],       # missing reps
])
def test_bad_input_raises(pairs):
    with pytest.raises(ValueError):
        parse_workout(form(*pairs), {1, 2})