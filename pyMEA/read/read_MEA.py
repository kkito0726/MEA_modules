from pyMEA import Calculator, CardioAveWave, FigMEA, FilterMEA
from pyMEA.core.Electrode import Electrode
from pyMEA.core.FilterType import FilterType
from pyMEA.core.PyMEA import PyMEA
from pyMEA.read.model.MEA import MEA


def read_MEA(
    hed_path: str,
    start: int,
    end: int,
    electrode_distance: int,
    filter_type=FilterType.NONE,
    front=0.05,
    back=0.3,
    distance=3000,
) -> PyMEA:
    if filter_type == FilterType.NONE:
        data = MEA(hed_path, start, end)
    elif filter_type == FilterType.CARDIO_AVE_WAVE:
        data = CardioAveWave(hed_path, start, end, front, back, distance)
    else:
        data = FilterMEA(hed_path, start, end)

    electrode = Electrode(electrode_distance)
    fig = FigMEA(data, electrode)
    calculator = Calculator(data, electrode_distance)

    return PyMEA(data, electrode, fig, calculator)
