from dundieplz.schemas.core_signals import ExtractedCoreSignals, Presence, Signal


def test_core_signals_instantiation():
    obj = ExtractedCoreSignals(
        suicidal_ideation=Signal(presence=Presence.indeterminate),
    )
    assert obj.suicidal_ideation.presence == Presence.indeterminate
