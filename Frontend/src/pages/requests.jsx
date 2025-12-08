import { useState } from "react";
import { useChat } from "../hooks/useChat";

export function Requests() {

  const { chat, loading, cameraZoomed, setCameraZoomed, message, setAnimationChat } = useChat();
    


  // FORMULARIO
  const [producto, setProducto] = useState("");
  const [fecha, setFecha] = useState("");
  const [modoAvanzado, setModoAvanzado] = useState(false);


  // RESPUESTAS
  const [respuesta, setRespuesta] = useState("");
  const [respuestaModelo, setRespuestaModelo] = useState(null);

  // ESTADOS
  // const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [predicciones, setPredicciones] = useState([]);

  // ---------- RESET ----------
  const reset = () => {
    setRespuesta("");
    setRespuestaModelo(null);
    setError("");
  };

  const limpiarPredicciones = () => {
    setPredicciones([]);
  };

  // ---------- API HELPERS ----------
  // Ajusta esta URL según tu backend
  const API_URL = "http://localhost:8000/api";

  const apiRequest = async (url, options = {}) => {
    try {
      setError("");

      const res = await fetch(url, options);

      if (!res.ok) throw new Error("Error de servidor");

      const data = await res.json();
      return data;

    } catch (err) {
      setError("Error conectando al servidor");
      return null;
    } finally {
      
    }
  };

  // ---------- MÉTODOS EQUIVALENTES A ANGULAR ----------

  

// producto + fecha
const predecirStockProducto = async () => {
  limpiarPredicciones();
  if (!producto || !fecha) {
    setError("Producto y fecha son obligatorios");
    return;
  }

  reset();

  const r = await apiRequest(`${API_URL}/predict/product-date`, {
    method: "POST",
    body: JSON.stringify({
      name: producto,
      date: fecha,
      llm: modoAvanzado
    }),
    headers: { "Content-Type": "application/json" },
  });

  if (r) {
    setRespuesta(JSON.stringify(r, null, 2));
    setRespuestaModelo(r);
  }

};

// todos los productos para una fecha
const predecirFechaCompleta = async () => {
  limpiarPredicciones();
  if (!fecha) {
    setError("La fecha es obligatoria");
    return;
  }

  reset();

  const r = await apiRequest(`${API_URL}/predict/date`, {
    method: "POST",
    body: JSON.stringify({
      date: fecha,
      llm: modoAvanzado
    }),
    headers: { "Content-Type": "application/json" }
  });

  if (r) {
    setRespuesta(JSON.stringify(r, null, 2));
    setPredicciones(r);
    setRespuestaModelo(r);
  }

};

// todos los productos hasta que alguno se agote
const productosEnRiesgo = async () => {
  limpiarPredicciones();
  reset();

  const r = await apiRequest(`${API_URL}/predict/all`, {
    method: "POST",
    body: JSON.stringify({ llm: modoAvanzado }),
    headers: { "Content-Type": "application/json" }
  });

  if (r) {
    setRespuesta(JSON.stringify(r, null, 2));
    setPredicciones(r);
    setRespuestaModelo(r);
  }
};

// un producto hasta agotarse
const predecirAgotamiento = async () => {
  limpiarPredicciones();
  if (!producto) {
    setError("Escribe un producto");
    return;
  }

  reset();

  const r = await apiRequest(`${API_URL}/predict/product`, {
    method: "POST",
    body: JSON.stringify({
      name: producto,
      llm: modoAvanzado
    }),
    headers: { "Content-Type": "application/json" }
  });

  if (r) {
    setRespuesta(JSON.stringify(r, null, 2));
    setPredicciones(r);
    setRespuestaModelo(r);
  }

};

// subir CSV
const subirCSV = async (event) => {
  limpiarPredicciones();
  const file = event.target.files[0];
  if (!file) return;

  reset();

  const form = new FormData();
  form.append("file", file);

  try {
    const res = await fetch(`${API_URL}/upload/retrain`, {
      method: "POST",
      body: form
    });

    if (!res.ok) throw new Error("Error subiendo CSV");

    const r = await res.json();
    setRespuesta("Modelo reentrenado.");
    setRespuestaModelo(r);
  } catch (err) {
    setError("Error subiendo CSV");
  } finally {
  }
};


  // ---------- RENDER ----------
  return (
    <div>
      <div className="border-b-8 border-[#ffb703] w-full"></div>

      <div className="px-10 py-10">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">

          {/* FORMULARIO */}
          <div>
            <h2 className="text-[#0f2c63] text-3xl font-bold text-center mb-8">
              Item
            </h2>

            <div className="space-y-8">

              <input
                type="text"
                placeholder="Producto"
                value={producto}
                onChange={(e) => setProducto(e.target.value)}
                className="border-2 border-[#0f2c63] rounded-3xl w-full px-6 py-3 text-xl"
              />

              <input
                type="date"
                value={fecha}
                onChange={(e) => setFecha(e.target.value)}
                className="border-2 border-[#0f2c63] rounded-3xl w-full px-6 py-3 text-xl"
              />

            </div>
            {/* SWITCH */}
            <div className="flex items-center mt-7 gap-4 mb-6 ">

              <span className="text-[#0f2c63] text-xl font-semibold">
                Utilizar LLM
              </span>

              <button
                onClick={() => setModoAvanzado(!modoAvanzado)}
                className={`
                  relative w-16 h-8 rounded-full transition-all duration-300
                  ${modoAvanzado ? "bg-[#0f2c63]" : "bg-gray-300"}
                `}
              >

                <span
                  className={`
                    absolute top-1 left-1 w-6 h-6 rounded-full bg-white shadow-md
                    transition-all duration-300
                    ${modoAvanzado ? "translate-x-8" : ""}
                  `}
                ></span>

              </button>
            </div>
          </div>

          {/* ACCIONES */}
          <div>
            <h2 className="text-[#0f2c63] text-3xl font-bold text-center mb-8">
              Acciones
            </h2>

            <div className="flex flex-col gap-5">

              <button
                onClick={predecirStockProducto}
                className="bg-[#0f2c63] text-white border-4 border-[#ffb703] rounded-full px-8 py-4 text-xl"
              >
                Predecir stock del producto
              </button>

              <button
                onClick={predecirFechaCompleta}
                className="bg-[#0f2c63] text-white border-4 border-[#ffb703] rounded-full px-8 py-4 text-xl"
              >
                Predicción completa por fecha
              </button>

              <button
                onClick={productosEnRiesgo}
                className="bg-[#0f2c63] text-white border-4 border-[#ffb703] rounded-full px-8 py-4 text-xl"
              >
                Productos en riesgo de agotarse
              </button>

              <button
                onClick={predecirAgotamiento}
                className="bg-[#0f2c63] text-white border-4 border-[#ffb703] rounded-full px-8 py-4 text-xl"
              >
                Fecha de agotamiento del producto
              </button>

              <label className="bg-[#0f2c63] cursor-pointer text-white border-4 border-[#ffb703] rounded-full px-8 py-4 text-xl text-center">
                Subir CSV / Reentrenar
                <input type="file" hidden onChange={subirCSV} />
              </label>

            </div>

            {/* RESULTADOS */}
            <div className="border-4 border-[#0f2c63] rounded-3xl p-6 text-[#0f2c63] text-xl text-center mt-8">
              
              {!loading && respuesta && <div>{respuesta}</div>}

              {loading && (
                <div className="animate-pulse">Procesando...</div>
              )}

              {error && (
                <div className="text-red-500">{error}</div>
              )}

            </div>

          </div>
        </div>

        {/* TABLA */}
        {predicciones.length > 0 && (
          <div className="mt-10 w-full md:w-10/12 lg:w-8/12 mx-auto">
            <h3 className="text-[#0f2c63] text-2xl font-semibold mb-4 text-center">
              Lista de predicciones
            </h3>

            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-300 rounded-xl shadow">
                <thead className="bg-[#0f2c63] text-white">
                  <tr>
                    <th className="px-6 py-3 text-left">Producto</th>
                    <th className="px-6 py-3 text-left">Stock Predicho</th>
                  </tr>
                </thead>

                <tbody>
                  {predicciones.map((p, index) => (
                    <tr key={index} className="border-b hover:bg-gray-100">
                      <td className="px-6 py-3">{p.product_name}</td>
                      <td className="px-6 py-3">{p.predicted_stock}</td>
                    </tr>
                  ))}
                </tbody>

              </table>
            </div>
          </div>
        )}

        <div className="mt-10">
          <input
            placeholder="Respuesta"
            className="border-2 border-[#0f2c63] rounded-3xl w-full px-6 py-4 text-xl"
            value={respuesta}
            readOnly
          />
        </div>
      </div>
    </div>
  );
}
