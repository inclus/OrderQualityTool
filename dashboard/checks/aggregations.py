from pydash import py_


def sum_aggregation(values):
    return py_(values).reject(lambda x: x is None).sum().value()


def avg_aggregation(values):
    return py_(values).reject(lambda x: x is None).mean().value()


def values_aggregation(values):
    return py_(values).reject(lambda x: x is None).value()


available_aggregations = {"SUM": sum_aggregation, "AVG": avg_aggregation, "VALUE": values_aggregation}