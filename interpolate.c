#include <Python.h>
#include <math.h>
/* UNUSED, Couldn't compile for Windows :( */
static PyObject* interpolate(PyObject* self, PyObject* args) {
    const Py_ssize_t tl = 2;
    const Py_ssize_t ll = 0;
    int nx, ny, angle, distance;
    if (!PyArg_ParseTuple(args, "iiii", &nx, &ny, &angle, &distance)) {
        return NULL;
    }
    PyObject* pos_list = PyList_New(ll);
    for (int i = 0; i < distance; i++) {
        double x = -i * cos(angle * M_PI / 180);
        double y =  i * sin(angle * M_PI / 180);
        PyObject *pos = Py_BuildValue("(ff)", x, y);
        PyList_Append(pos_list, pos);
    }
    return pos_list;
}

static PyMethodDef gameMathMethods[] = {
    {"interpolate",  interpolate, METH_VARARGS,
     "interpolate(nx, ny, angle, distance) -> [(x0, y0), (x1, y1), ...]"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef gameMathmodule = {
    PyModuleDef_HEAD_INIT,
    "gameMath",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    gameMathMethods
};

PyMODINIT_FUNC
PyInit_gameMath(void)
{
    return PyModule_Create(&gameMathmodule);
}