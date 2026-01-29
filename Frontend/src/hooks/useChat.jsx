import { createContext, useContext, useEffect, useState } from "react";

const backendUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState();
  const [loading, setLoading] = useState(false);
  const [cameraZoomed, setCameraZoomed] = useState(true);
  
 const chat = async (text) => {
    setLoading(true);
    console.log("Datos enviados:", text);
    
    try {
      const data = await fetch(`${backendUrl}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }), // Asegúrate de que el backend reciba "message"
      });

      const response = await data.json();
      
      // 'resp' suele ser el array de mensajes que devuelve el backend (con audio, texto, etc.)
      const resp = response.messages || response.text; 
      
      const newResponseMessage = {
        text: resp,
        
      };
      // Actualizamos la cola de mensajes
      // Esto hará que el useEffect en ChatContext asigne el primer mensaje a 'message'
      // Y a su vez, el useEffect en tu componente Llm detecte ese 'message'
      console.log(resp) // // esto es igual a texto de respuesta
      setMessages((prev) => [...prev, newResponseMessage]);

    } catch (error) {
      console.error("Error en chat:", error);
    } finally {
      setLoading(false);
    }
  };
  
  const onMessagePlayed = () => {
    setMessages((messages) => messages.slice(1));
  };

  useEffect(() => {
    if (messages.length > 0) {
      setMessage(messages[0]);
    } else {
      setMessage(null);
    }
  }, [messages]);

  return (
    <ChatContext.Provider
      value={{
        chat,
        message,
        onMessagePlayed,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};