#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>


// ---------------- GLOBALS ------------------------


typedef struct ASCIIImage{
    PyObject_HEAD
    const char* data;
    unsigned short int width;
    unsigned short int height;
    unsigned char style_code;
} ASCIIImage;


static void ASCIIImage_dealloc(ASCIIImage* self) {
    Py_TYPE(self)->tp_free((PyObject*)self);
}


static PyObject* ASCIIImage_new(PyTypeObject* type, PyObject* args, PyObject* kwds) {
    ASCIIImage* self;
    self = (ASCIIImage*)type->tp_alloc(type, 0);
    return (PyObject*)self;
}


static int ASCIIImgage_init(ASCIIImage* self, PyObject* args, PyObject* kwds) {
    static char* kwlist[] = {"data", "width", "height", "style_code", NULL};
    const char* data;
    const unsigned short int width;
    const unsigned short int height;
    const unsigned char style_code;

    if (!PyArg_ParseTupleAndKeywords(args, kwds,
        "sHHb",
        kwlist,
        &data, &width, &height, &style_code
    )) {
        return -1;
    }

    self->data = data;
    self->width = width;
    self->height = height;
    self->style_code = style_code;

    return 0;
}


static PyObject* ASCIIImage_get_data(ASCIIImage* self, void* closure) {
    return PyUnicode_FromString(self->data);
}


static PyObject* ASCIIImage_get_width(ASCIIImage* self, void* closure) {
    return PyLong_FromUnsignedLong(self->width);
}


static PyObject* ASCIIImage_get_height(ASCIIImage* self, void* closure) {
    return PyLong_FromUnsignedLong(self->height);
}


static PyObject* ASCIIImage_get_style_code(ASCIIImage* self, void* closure) {
    return PyLong_FromUnsignedLong(self->style_code);
}


static PyGetSetDef ASCIIImage_getsetters[] = {
    {"data", (getter)ASCIIImage_get_data, NULL, "data", NULL},
    {"width", (getter)ASCIIImage_get_width, NULL, "width", NULL},
    {"height", (getter)ASCIIImage_get_height, NULL, "height", NULL},
    {"style_code", (getter)ASCIIImage_get_style_code, NULL, "style_code", NULL},
    {NULL}
};


static PyMemberDef ASCIIImage_members[] = {
    {"data", T_STRING, offsetof(ASCIIImage, data), 0, "data"},
    {"width", T_SHORT, offsetof(ASCIIImage, width), 0, "width"},
    {"height", T_SHORT, offsetof(ASCIIImage, height), 0, "height"},
    {"style_code", T_UBYTE, offsetof(ASCIIImage, style_code), 0, "style_code"},
    {NULL}
};


static PyTypeObject ASCIIImageType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "c_ascii_converter.ASCIIImage",
    .tp_doc = "ASCIIImage(data: str, width: int, height: int, style_code: int)",
    .tp_basicsize = sizeof(ASCIIImage),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = ASCIIImage_new,
    .tp_dealloc = (destructor) ASCIIImage_dealloc,
    .tp_init = (initproc) ASCIIImgage_init,
    .tp_members = ASCIIImage_members,
    .tp_getset = ASCIIImage_getsetters,
};


// ---------------- ASCII CONVERTER ----------------


#define CHARACTERS_NUMBER 8
// The ASCII characters to be printed
const char CHARACTERS[CHARACTERS_NUMBER] = {' ', '.', '-', '*', 'o', 'O', '#', '@'};

// Maximum value of the RGB channels
const unsigned char MAX_CHANNEL_INTENSITY = 255;
const unsigned short MAX_CHANNEL_VALUES = MAX_CHANNEL_INTENSITY * 3; // 3 is the number of channels of a Pixel (red, green, blue)

// Some useful type definitions

// Pixel is an array of bytes (unsigned char) representing the RGB values of a pixel
typedef unsigned char* Pixel;
    

// Associates a pixel intensity to an ASCII character
static char mapIntensityToCharacter(float intensity) {
    return CHARACTERS[(int) roundf(intensity * (CHARACTERS_NUMBER - 1))];
}


// Converts a pixel to a floating point intensity
static float getPixelIntensity(Pixel pixel) {
    return (float) (pixel[0] + pixel[1] + pixel[2]) / MAX_CHANNEL_VALUES;
}


static PyObject* convert_frame(PyObject* self, PyObject* args)
{
    // Declare the arguments that will be passed by Python
    PyBytesObject* frameBytes;
    unsigned short frameWidth;
    unsigned short frameHeight;
    
    // Parse the arguments
    if (!PyArg_ParseTuple(args, "SHH", &frameBytes, &frameWidth, &frameHeight)) {
        printf("Error parsing arguments for convert_frame\n");
        return NULL;
    }

    // Get the frame data
    Py_buffer pyBuffer;
    if (PyObject_GetBuffer((PyObject*) frameBytes, &pyBuffer, PyBUF_READ) < 0) {
        printf("Error getting buffer from frame\n");
        return NULL;
    }

    const unsigned char* frameBuffer = pyBuffer.buf;
    // Each pixel is composed of 3 channels
    const unsigned short BUFFER_WIDTH = frameWidth * 3;

    // Create the string to store the frame that will be returned
    char string[frameHeight * frameWidth];

    // Iterate over the rows of the frame and convert them to ASCII
    unsigned int yString = 0;
    for (unsigned short y = 0; y < frameHeight; y++, yString += frameWidth) {

        for (unsigned short xBuffer = 0, xString = 0; xString < frameWidth; xBuffer+=3, xString++) {
            // Calculate the position of the pixel in the frame
            const unsigned int framePosition = y * BUFFER_WIDTH + xBuffer;
            
            // Calculate the intensity of the pixel by its RGB values
            const float intensity = getPixelIntensity((Pixel) &frameBuffer[framePosition]);
            
            // Convert the intensity to a character using the CHARAACTERS lookup table
            const char character = mapIntensityToCharacter(intensity);
            
            // Store the character in the string
            string[yString + xString] = character;
        }
        // Add a new line after each row
        string[yString + frameWidth - 1] = '\n';
    }
    // Add the null termination character at the end of the string
    string[frameHeight * frameWidth - 1] = '\0';

    // Release the previously allocated buffer to avoid memory leaks
    PyBuffer_Release(&pyBuffer);

    // return a Python string representing the frame
    return Py_BuildValue("s", string);
}



// ---------------- FRAME COMPRESSION  -------------------


#define MULTI_CHAR_SIGN 0
#define NEWLINE_CHAR_CODE 10
#define MULTI_CHAR_SEQUENCE_LENGTH 3 // Sequence: 0x00 | count | char
#define HEADER_SIZE 5 // Size of the header of a compressed frame


static void multiChar(unsigned char character, size_t count, unsigned char* buffer) {
    buffer[0] = MULTI_CHAR_SIGN;
    buffer[1] = (unsigned char) count;
    buffer[2] = character;
}


static PyObject* compress_frame(PyObject* self, PyObject* args)
{
    const char* frame;
    unsigned short frameWidth;
    unsigned short frameHeight;
    unsigned char frameStyleCode;

    if (!PyArg_ParseTuple(args, "sHHB", &frame, &frameWidth, &frameHeight, &frameStyleCode)) {
        printf("Error parsing arguments for compress_frame\n");
        return NULL;
    }

    const size_t frameSize = (frameWidth + 1) * frameHeight;

    // Create the buffer to store the compressed frame
    unsigned char buffer[frameSize];

    char currentChar = frame[0];
    size_t count = 1;
    size_t bufferIndex = 0;
    // Start from frameIndex 1 because currentChar is already set to the first character of the frame
    for (size_t frameIndex = 1; frameIndex < frameSize; frameIndex++) {
        const char c = frame[frameIndex];

        if (currentChar == c) {
            count ++;
            if (count == 255) {
                multiChar((unsigned char) c, 255, buffer + bufferIndex);
                count = 1;
                bufferIndex += MULTI_CHAR_SEQUENCE_LENGTH;
            }
        }
        else if (count < 4) {
            // Add <count> characters to the buffer
            for (unsigned char i = 0; i < count; i++) {
                buffer[bufferIndex + i] = (unsigned char) currentChar;
            }
            bufferIndex += count;
            count = 1;
            currentChar = c;
        }
        else {
            multiChar((unsigned char) currentChar, count, buffer + bufferIndex);
            bufferIndex += MULTI_CHAR_SEQUENCE_LENGTH;
            count = 1;
            currentChar = c;
        }

    }

    // Add the last character to the buffer
    if (count < 4) {
        for (unsigned char i = 0; i < count; i++) {
            buffer[bufferIndex + i] = (unsigned char) currentChar;
        }
        bufferIndex += count;
    }
    else {
        multiChar((unsigned char) currentChar, count, buffer + bufferIndex);
        bufferIndex += MULTI_CHAR_SEQUENCE_LENGTH;
    }

    // Create a new buffer to store the compressed frame
    unsigned char compressedFrame[bufferIndex + HEADER_SIZE];

    // Create the header right into the compressed frame to avoid copying the header into the buffer
    compressedFrame[0] = frameStyleCode;
    compressedFrame[1] = (unsigned char) (frameWidth >> 8);
    compressedFrame[2] = (unsigned char) (frameWidth & 0xFF);
    compressedFrame[3] = (unsigned char) (frameHeight >> 8);
    compressedFrame[4] = (unsigned char) (frameHeight & 0xFF);

    // Copy the compressed frame buffer into the new, final buffer
    memcpy(compressedFrame + HEADER_SIZE, buffer, bufferIndex);
    
    // Return a Python bytes object representing the compressed frame
    return Py_BuildValue("y#", compressedFrame, bufferIndex + HEADER_SIZE);   
}


// ---------------- FRAME DECOMPRESSION  -------------------


static PyObject* decompress_frame(PyObject* self, PyObject* args)
{
    PyBytesObject* compressedFrame;

    if (!PyArg_ParseTuple(args, "S", &compressedFrame)) {
        printf("Error parsing arguments for decompress_frame\n");
        return NULL;
    }

    // Get the compressed frame data
    Py_buffer pyBuffer;
    if (PyObject_GetBuffer((PyObject*) compressedFrame, &pyBuffer, PyBUF_READ) < 0) {
        printf("Error getting buffer from frame\n");
        return NULL;
    }

    const unsigned char* buffer = pyBuffer.buf;
    const size_t bufferSize = pyBuffer.len;

    // Extract the header from the compressed frame buffer
    const unsigned char styleCode = buffer[0];
    const unsigned short frameWidth = (buffer[1] << 8) | buffer[2];
    const unsigned short frameHeight = (buffer[3] << 8) | buffer[4];

    // Calculate the size of the uncompressed frame
    const size_t frameSize = (frameWidth + 1) * frameHeight;

    // Create the buffer to store the uncompressed frame
    // +1 to store the null termination character
    char uncompressedFrame[frameSize + 1];
    uncompressedFrame[frameSize] = '\0';

    // Start from bufferIndex HEADER_SIZE because the header is already extracted
    size_t bufferIndex = HEADER_SIZE;
    size_t frameIndex = 0;

    while (frameIndex < frameSize) {
        const unsigned char byte = buffer[bufferIndex];

        printf("Byte: %d, index: %ld\n", byte, frameIndex);

        if (byte == MULTI_CHAR_SIGN) {
            // Extract the count and the character from the buffer
            const size_t count = buffer[bufferIndex + 1];
            const unsigned char character = buffer[bufferIndex + 2];

            // Add <count> characters to the buffer
            for (unsigned char i = 0; i < count; i++) {
                uncompressedFrame[frameIndex + i] = character;
            }
            bufferIndex += MULTI_CHAR_SEQUENCE_LENGTH;
            frameIndex += count;
        }
        else {
            // Add the character to the buffer
            uncompressedFrame[frameIndex] = byte;
            bufferIndex ++;
            frameIndex ++;
        }

    }

    // Release the previously allocated buffer to avoid memory leaks
    PyBuffer_Release(&pyBuffer);

    // Return a Python tuple containing the image data, width, height and style code
    return Py_BuildValue("sHHB", uncompressedFrame, frameWidth, frameHeight, styleCode);
}
    


// ---------------- MODULE INITIALIZATION ----------------


// Define the functions that will be exported to Python
static PyMethodDef module_methods[] = 
{
    {"convert_frame", convert_frame, METH_VARARGS, "Convert an image into an ASCII string"},
    {"compress_frame", compress_frame, METH_VARARGS, "Compress an ASCII string into an array of bytes with metadata"},
    {"decompress_frame", decompress_frame, METH_VARARGS, "Decompress an array of bytes with metadata into an ASCII string"},
    {NULL} // this struct signals the end of the array
};


// Struct representing the module
static PyModuleDef c_module =
{
    PyModuleDef_HEAD_INIT, // PyModuleDef_HEAD_INIT should always be the first element of the struct
    .m_name = "c_ascii_converter", // Module name
    .m_doc = "Convert an image to ASCII characters.", // module description
    .m_size = -1, // Module size (https://docs.python.org/3/extending/extending.html)
    .m_methods = module_methods // Methods associated with the module
};


// The initialization function that will be called when the module is loaded
PyMODINIT_FUNC PyInit_c_ascii_converter()
{
    PyObject *m;
    if (PyType_Ready(&ASCIIImageType) < 0)
        return NULL;

    m = PyModule_Create(&c_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&ASCIIImageType);
    if (PyModule_AddObject(m, "ASCIIImage", (PyObject *) &ASCIIImageType) < 0) {
        Py_DECREF(&ASCIIImageType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
