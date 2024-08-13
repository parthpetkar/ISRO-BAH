import './App.css';
import gptLogo from './assets/chatgpt1.png';
import addBtn from './assets/add-30.png';
import sendBtn from './assets/send.svg';
import userIcon from './assets/my-face.jpg';
import gptImgLogo from './assets/chat_bot_icon.jpeg';
import { useEffect, useRef, useState } from 'react';
import { saveChatToCache, saveCacheToDb, fetchChatFromDb, fetchChats } from './services/api';

function App() {
  const msgEnd = useRef(null);
  const [input, setInput] = useState("");
  const [option, setOption] = useState("Generation");
  const [messages, setMessages] = useState([]);
  const [chatId, setChatId] = useState(null);
  const [previousChats, setPreviousChats] = useState([]);
  const [similarQuestion, setSimilarQuestion] = useState("");
  const [previousResponses, setPreviousResponses] = useState([]);

  useEffect(() => {
    msgEnd.current.scrollIntoView();
  }, [messages]);

  useEffect(() => {
    const loadChats = async () => {
      try {
        const chats = await fetchChats();
        setPreviousChats(chats);
      } catch (error) {
        console.error('Error loading chats', error);
      }
    };
    loadChats();
  }, []);

  const clearSimilarQuestion = () => {
    setSimilarQuestion("");
  };

  const handleSend = async () => {
    const text = input;
    setInput('');

    const userMessage = { text, isBot: false, option };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setPreviousResponses(prevResponses => [...prevResponses, userMessage]);

    try {
      const response = await saveChatToCache([userMessage]);

      if (!response || !response.chat_data || !Array.isArray(response.chat_data)) {
        throw new Error('Unexpected API response format');
      }

      const chatData = response.chat_data;
      const similarQ = response.similar_question || "";

      setSimilarQuestion(similarQ);

      const botResponses = chatData.filter(msg => msg.isBot);
      if (botResponses.length > 0) {
        const botMessages = botResponses.map(botResponse => ({
          text: botResponse.text,
          isBot: true,
          option
        }));
        setMessages(prevMessages => [...prevMessages, ...botMessages]);
        setPreviousResponses(prevResponses => [...prevResponses, ...botMessages]);

      // clearSimilarQuestion();
      } else {
        console.error('No bot response found');
      }
    } catch (error) {
      console.error('Error during chat processing:', error.message);

      const errorMessage = { text: "Error processing message", isBot: true, option };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
      setPreviousResponses(prevResponses => [...prevResponses, errorMessage]);

      clearSimilarQuestion();
    }
  };

  const handleEnter = async (e) => {
    if (e.key === 'Enter') await handleSend();
  };

  const handleNewChat = async () => {
    try {
      if (messages.length > 0) {
        await saveCacheToDb(chatId);
      }
    } catch (error) {
      console.error('Error saving cache to db', error);
    }

    setMessages([]);
    setChatId(null);
    setSimilarQuestion("");
    setPreviousResponses([]);

    try {
      const updatedChats = await fetchChats();
      setPreviousChats(updatedChats);
    } catch (error) {
      console.error('Error loading updated chats', error);
    }
  };

  const loadPreviousChat = async (id) => {
    try {
      const chatData = await fetchChatFromDb(id);
      setMessages(chatData);
      setPreviousResponses(chatData);
      setChatId(id);
      setSimilarQuestion("");
    } catch (error) {
      console.error('Error fetching chat from db', error);
    }
  };

  return (
    <div className="App">
      <div className="sidebar">
        <div className="fixedContent">
          <img src={gptLogo} alt='logo' className='logo' /><span className='brand'></span>
          <button className='midBtn' onClick={handleNewChat}><img src={addBtn} alt='new chat' className='addBtn' />New Chat</button>
        </div>
        <div className="scrollableContent">
          {previousChats.map((chat) => (
            <button key={chat.id} className='query' onClick={() => loadPreviousChat(chat.id)}>
              Chat {chat.id} - {new Date(chat.created_at).toLocaleString()}
            </button>
          ))}
        </div>
      </div>

      <div className='main'>
        <div className='chats scrollableContent'>
          {previousResponses.map((message, i) =>
            <div key={i} className={message.isBot ? 'chat bot' : 'chat'}>
              <img className='chatImg' src={message.isBot ? gptImgLogo : userIcon} alt='' /><p className='txt'>{message.text}</p>
            </div>
          )}
          <div ref={msgEnd}></div>
        </div>

        <div className='chatFooter'>
          {similarQuestion && (
            <div className='similarQuestion' onClick={() => setInput(similarQuestion)}>
              Similar Question: {similarQuestion}
            </div>
          )}
          <div className='inp'>
            <select value={option} onChange={(e) => setOption(e.target.value)}>
              <option value="Generation">Generation</option>
              <option value="Retrieval">Retrieval</option>
              <option value="Comparative">Comparative</option>
            </select>
            <input type='text' placeholder='Send a message' value={input} onKeyDown={handleEnter} onChange={(e) => setInput(e.target.value)} />
            <button className='send' onClick={handleSend}><img src={sendBtn} alt='send' /></button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
