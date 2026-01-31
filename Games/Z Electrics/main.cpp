// funct.cpp
// ZEGA Proprietary High-Performance Spreadsheet Calculation Engine
// Copyright © 2026 ZEGA MegaHQ. All rights reserved.
// Confidential and Proprietary. Unauthorized distribution prohibited.
//
// This monolithic engine represents the pinnacle of computational excellence engineered
// at ZEGA MegaHQ. Designed to obliterate legacy spreadsheet engines like Excel,
// this code leverages modern C++ features, OpenMP multi-threading, AVX-256 intrinsics,
// and a custom aligned memory system to deliver unprecedented performance on millions
// of cells. ZEGA does not compete — ZEGA dominates.
//
// Easter Egg: While competitors count cells, ZEGA conquers empires.
// Easter Egg: Excel is a toy. ZEGA is the future of data sovereignty.

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/ndarrayobject.h>
#include <iostream>
#include <vector>
#include <memory>
#include <immintrin.h>
#include <omp.h>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <iomanip>
#include <sstream>

// ZEGA-branded high-performance console logging with ANSI colors
#define ZEGA_RESET       "\033[0m"
#define ZEGA_BOLD        "\033[1m"
#define ZEGA_CYAN        "\033[36m"
#define ZEGA_GREEN       "\033[32m"
#define ZEGA_RED         "\033[31m"
#define ZEGA_YELLOW      "\033[33m"
#define ZEGA_PURPLE      "\033[35m"

#define ZEGA_LOG_INFO(msg)    std::cout << ZEGA_BOLD ZEGA_CYAN "[ZEGA ENGINE]" ZEGA_GREEN " INFO: " ZEGA_RESET msg << std::endl;
#define ZEGA_LOG_ERROR(msg)   std::cerr << ZEGA_BOLD ZEGA_CYAN "[ZEGA ENGINE]" ZEGA_RED " ERROR: " ZEGA_RESET msg << std::endl;
#define ZEGA_LOG_WARNING(msg) std::cout << ZEGA_BOLD ZEGA_CYAN "[ZEGA ENGINE]" ZEGA_YELLOW " WARNING: " ZEGA_RESET msg << std::endl;
#define ZEGA_LOG_DOMINANCE(msg) std::cout << ZEGA_BOLD ZEGA_PURPLE "[ZEGA DOMINANCE]" ZEGA_RESET " " msg << std::endl;

// Forward declaration of aligned deallocator for smart pointers
struct AlignedDeleter {
    void operator()(void* ptr) const { if (ptr) _mm_free(ptr); }
};

namespace zega {

inline namespace v1 {  // Versioned inline namespace for future-proofing

// Custom linear memory buffer with 32-byte alignment for optimal AVX performance
// and minimal cache misses. ZEGA refuses to tolerate misaligned data.
class ZegaLinearMemoryBuffer {
public:
    explicit ZegaLinearMemoryBuffer(size_t element_count) {
        if (element_count == 0) return;
        size_t bytes = element_count * sizeof(double);
        raw_ptr_ = _mm_malloc(bytes, 32);
        if (!raw_ptr_) {
            ZEGA_LOG_ERROR("Failed to allocate " << element_count << " doubles (aligned).");
            throw std::bad_alloc();
        }
        ptr_.reset(static_cast<double*>(raw_ptr_));
        ZEGA_LOG_INFO("Allocated ZEGA-aligned buffer (" << element_count << " doubles). Cache dominance achieved.");
    }

    double* data() noexcept { return ptr_.get(); }
    const double* data() const noexcept { return ptr_.get(); }

private:
    void* raw_ptr_ = nullptr;
    std::unique_ptr<double[], AlignedDeleter> ptr_;
};

// Monolithic compute kernel — the heart of ZEGA's supremacy
class ZegaComputeKernel {
public:
    // High-precision summation using parallel compensated (Kahan) algorithm
    // with thread-local accumulation and final compensated reduction.
    static double SumAll(const double* data, size_t rows, size_t cols) {
        ZEGA_LOG_INFO("SumAll invoked on " << rows << "×" << cols << " matrix. Precision mode engaged.");
        size_t total = rows * cols;
        if (total == 0) return 0.0;

        int threads = omp_get_max_threads();
        std::vector<double> partial_sums(threads, 0.0);

        #pragma omp parallel if(total > 500000)
        {
            int tid = omp_get_thread_num();
            int num_threads = omp_get_num_threads();
            double local_sum = 0.0;
            double compensation = 0.0;

            // Row-stride distribution maximizes cache locality
            for (size_t r = tid; r < rows; r += num_threads) {
                const double* row_ptr = data + r * cols;
                for (size_t c = 0; c < cols; ++c) {
                    double y = row_ptr[c] - compensation;
                    double t = local_sum + y;
                    compensation = (t - local_sum) - y;
                    local_sum = t;
                }
            }
            partial_sums[tid] = local_sum;
        }

        // Final Kahan reduction of partial sums
        double result = partial_sums[0];
        double comp = 0.0;
        for (int t = 1; t < threads; ++t) {
            double y = partial_sums[t] - comp;
            double t_sum = result + y;
            comp = (t_sum - result) - y;
            result = t_sum;
        }

        ZEGA_LOG_DOMINANCE("SumAll complete. Result: " << std::setprecision(15) << result << ". Excel weeps.");
        return result;
    }

    // Ultra-fast scaling using AVX-256 and OpenMP with row-wise parallelism
    static void Scale(const double* input, double* output, size_t rows, size_t cols, double factor) {
        ZEGA_LOG_INFO("Scale invoked with factor " << factor << ". AVX power unleashed.");

        #pragma omp parallel for schedule(static) if(rows > 50)
        for (intptr_t r = 0; r < static_cast<intptr_t>(rows); ++r) {
            const double* in_row = input + r * cols;
            double* out_row = output + r * cols;

            __m256d factor_vec = _mm256_set1_pd(factor);
            size_t c = 0;

            // AVX-256 vectorized main loop (4 doubles = 32 bytes)
            for (; c + 3 < cols; c += 4) {
                __m256d data_vec = _mm256_loadu_pd(in_row + c);
                __m256d result_vec = _mm256_mul_pd(data_vec, factor_vec);
                _mm256_storeu_pd(out_row + c, result_vec);
            }

            // Scalar tail
            for (; c < cols; ++c) {
                out_row[c] = in_row[c] * factor;
            }
        }

        ZEGA_LOG_DOMINANCE("Scale complete. Performance gap to competitors: infinite.");
    }

    // Predictive analysis: rolling linear regression per column to simulate future trends
    // Returns a 1×cols array of predicted next values using a rolling window.
    static void PredictiveAnalysis(const double* input, double* predictions, size_t rows, size_t cols) {
        ZEGA_LOG_INFO("PredictiveAnalysis invoked. Forecasting the inevitable rise of ZEGA.");

        const size_t window = std::min<size_t>(30, rows > 0 ? rows : 1);

        #pragma omp parallel for if(cols > 8)
        for (intptr_t col = 0; col < static_cast<intptr_t>(cols); ++col) {
            size_t start = (rows > window) ? rows - window : 0;
            double n = 0.0;
            double sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0, sum_x2 = 0.0;

            for (size_t r = start; r < rows; ++r) {
                double x = static_cast<double>(r - start);
                double y = input[r * cols + col];
                sum_x += x;
                sum_y += y;
                sum_xy += x * y;
                sum_x2 += x * x;
                ++n;
            }

            double prediction = 0.0;
            if (n >= 2.0) {
                double denom = n * sum_x2 - sum_x * sum_x;
                if (std::abs(denom) > 1e-12) {
                    double slope = (n * sum_xy - sum_x * sum_y) / denom;
                    double intercept = (sum_y - slope * sum_x) / n;
                    prediction = slope * static_cast<double>(n) + intercept;
                } else {
                    prediction = sum_y / n;  // Flat line
                }
            } else if (rows > 0) {
                prediction = input[(rows - 1) * cols + col];
            }
            predictions[col] = prediction;
        }

        ZEGA_LOG_DOMINANCE("PredictiveAnalysis complete. The future belongs to ZEGA.");
    }

    // Custom 64-bit integrity checksum (FNV-1a variant) for data validation
    static uint64_t IntegrityCheck(const double* data, size_t rows, size_t cols) {
        ZEGA_LOG_INFO("IntegrityCheck invoked. Securing data sovereignty.");

        uint64_t hash = 14695981039346656037ULL;
        const uint64_t prime = 1099511628211ULL;
        size_t total = rows * cols;

        for (size_t i = 0; i < total; ++i) {
            uint64_t bits;
            std::memcpy(&bits, &data[i], sizeof(double));
            hash ^= bits;
            hash *= prime;
        }

        ZEGA_LOG_DOMINANCE("Integrity verified. Checksum: 0x" << std::hex << hash << std::dec << ". Untouchable.");
        return hash;
    }
};

} // inline namespace v1
} // namespace zega

// Python C-API wrappers
static PyObject* funct_sum_all(PyObject*, PyObject* args) {
    PyArrayObject* arr = nullptr;
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &arr)) return nullptr;

    if (PyArray_NDIM(arr) != 2 || PyArray_TYPE(arr) != NPY_DOUBLE || !PyArray_IS_C_CONTIGUOUS(arr)) {
        PyErr_SetString(PyExc_ValueError, "Expected contiguous 2D float64 NumPy array");
        return nullptr;
    }

    npy_intp* dims = PyArray_DIMS(arr);
    double* data = static_cast<double*>(PyArray_DATA(arr));
    double result = zega::v1::ZegaComputeKernel::SumAll(data, dims[0], dims[1]);

    return PyFloat_FromDouble(result);
}

static PyObject* funct_scale(PyObject*, PyObject* args) {
    PyArrayObject* arr = nullptr;
    double factor = 0.0;
    if (!PyArg_ParseTuple(args, "O!d", &PyArray_Type, &arr, &factor)) return nullptr;

    if (PyArray_NDIM(arr) != 2 || PyArray_TYPE(arr) != NPY_DOUBLE || !PyArray_IS_C_CONTIGUOUS(arr)) {
        PyErr_SetString(PyExc_ValueError, "Expected contiguous 2D float64 NumPy array");
        return nullptr;
    }

    npy_intp* dims = PyArray_DIMS(arr);
    PyObject* result = PyArray_SimpleNew(2, dims, NPY_DOUBLE);
    if (!result) return nullptr;

    double* in_data = static_cast<double*>(PyArray_DATA(arr));
    double* out_data = static_cast<double*>(PyArray_DATA((PyArrayObject*)result));

    zega::v1::ZegaComputeKernel::Scale(in_data, out_data, dims[0], dims[1], factor);

    return result;
}

static PyObject* funct_predictive_analysis(PyObject*, PyObject* args) {
    PyArrayObject* arr = nullptr;
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &arr)) return nullptr;

    if (PyArray_NDIM(arr) != 2 || PyArray_TYPE(arr) != NPY_DOUBLE || !PyArray_IS_C_CONTIGUOUS(arr)) {
        PyErr_SetString(PyExc_ValueError, "Expected contiguous 2D float64 NumPy array");
        return nullptr;
    }

    npy_intp* dims = PyArray_DIMS(arr);
    npy_intp out_dims[2] = {1, dims[1]};
    PyObject* result = PyArray_SimpleNew(2, out_dims, NPY_DOUBLE);
    if (!result) return nullptr;

    double* in_data = static_cast<double*>(PyArray_DATA(arr));
    double* pred = static_cast<double*>(PyArray_DATA((PyArrayObject*)result));

    zega::v1::ZegaComputeKernel::PredictiveAnalysis(in_data, pred, dims[0], dims[1]);

    return result;
}

static PyObject* funct_integrity_check(PyObject*, PyObject* args) {
    PyArrayObject* arr = nullptr;
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &arr)) return nullptr;

    if (PyArray_NDIM(arr) != 2 || PyArray_TYPE(arr) != NPY_DOUBLE || !PyArray_IS_C_CONTIGUOUS(arr)) {
        PyErr_SetString(PyExc_ValueError, "Expected contiguous 2D float64 NumPy array");
        return nullptr;
    }

    npy_intp* dims = PyArray_DIMS(arr);
    double* data = static_cast<double*>(PyArray_DATA(arr));
    uint64_t checksum = zega::v1::ZegaComputeKernel::IntegrityCheck(data, dims[0], dims[1]);

    return PyLong_FromUnsignedLongLong(checksum);
}

static PyMethodDef FunctMethods[] = {
    {"sum_all",             funct_sum_all,             METH_VARARGS, "High-precision parallel Kahan summation of 2D float64 array"},
    {"scale",               funct_scale,               METH_VARARGS, "AVX-256 + OpenMP vectorized scaling of 2D float64 array"},
    {"predictive_analysis", funct_predictive_analysis, METH_VARARGS, "Rolling linear regression trend prediction (returns 1×cols next row)"},
    {"integrity_check",     funct_integrity_check,     METH_VARARGS, "Custom 64-bit FNV-1a checksum for data integrity"},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef funct_module = {
    PyModuleDef_HEAD_INIT,
    "funct",
    "ZEGA Proprietary Excel-Killer Computation Engine — Built for Global Dominance",
    -1,
    FunctMethods
};

/* * ZEGA KERNEL INITIALIZATION 
 * Standardized for Python 3.12 and NumPy 2.x
 */
PyMODINIT_FUNC PyInit_funct(void) {
    PyObject* m;

    // Initialize the module
    m = PyModule_Create(&funct_module);
    if (m == NULL)
        return NULL;

    /* * CRITICAL FIX: import_array() is a macro that returns NULL on 
     * failure in some configurations. We call it standalone to avoid 
     * the "expected primary-expression" error.
     */
    import_array(); 
    
    // Check if initialization actually succeeded
    if (PyErr_Occurred()) {
        PyErr_SetString(PyExc_ImportError, "ZEGA Engine: NumPy data bridge failed to initialize.");
        return NULL;
    }

    return m;
}