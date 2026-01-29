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
    
    try {
      const data = await fetch(`${backendUrl}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });

      const response = await data.json();
      
      // Obtenemos el texto (ya sea de response.messages[0].text o response.text)
      const textContent = response.messages ? response.messages[0].text : response.text;

      const newResponseMessage = {
        text: textContent,
      };

      // Reemplazamos la lista para que solo contenga el nuevo mensaje
      // Esto asegura que el useEffect tome este y solo este mensaje
      setMessages([newResponseMessage]);

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