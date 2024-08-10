import './App.css';
import gptLogo from './assets/chatgpt1.png';
import addBtn from './assets/add-30.png';
import sendBtn from './assets/send.svg';
// import userIcon from './assets/user-icon.png';
import userIcon from './assets/my-face.jpg'
import gptImgLogo from './assets/chat_bot_icon.jpeg';
import { useEffect, useRef, useState } from 'react';
import { saveChatToCache, saveCacheToDb, fetchChatFromDb, fetchChats } from './services/api';

function App() {
  const msgEnd = useRef(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [chatId, setChatId] = useState(null);
  const [previousChats, setPreviousChats] = useState([]);

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

  const handleSend = async () => {
    const text = input;
    setInput('');
    const userMessage = { text, isBot: false };
    setMessages(prevMessages => [...prevMessages, userMessage]);

    // Simulate a bot response (replace with actual bot response logic)
    const botResponse = "This is a simulated response.";
    const newMessages = [
      ...messages,
      userMessage,
      { text: botResponse, isBot: true }
    ];
    setMessages(newMessages);

    // Save chat to cache
    try {
      await saveChatToCache(newMessages);
    } catch (error) {
      console.error('Error saving chat to cache', error);
    }
  };

  const handleEnter = async (e) => {
    if (e.key === 'Enter') await handleSend();
  };

  const handleNewChat = async () => {
    try {
      if (messages.length > 0) {
        const response = await saveCacheToDb(chatId);  // Pass chatId correctly
        if (response.chat_id) {
          setChatId(response.chat_id);  // Update chatId if a new one is created
        }
      }
    } catch (error) {
      console.error('Error saving cache to db', error);
    }

    // Clear current messages
    setMessages([]);
    setChatId(null);

    // Fetch updated chat list
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
      setChatId(id);
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
          {messages.map((message, i) =>
            <div key={i} className={message.isBot ? 'chat bot' : 'chat'}>
              <img className='chatImg' src={message.isBot ? gptImgLogo : userIcon} alt='' /><p className='txt'>{message.text}</p>
            </div>
          )}
          <div ref={msgEnd}></div>
        </div>

        <div className='chatFooter'>
          <div className='inp'>
            <input type='text' placeholder='Send a message' value={input} onKeyDown={handleEnter} onChange={(e) => { setInput(e.target.value) }} /> <button className='send' onClick={handleSend}><img src={sendBtn} alt='send' /></button>
          </div>
          {/* <p>Chat may produce incorrect results</p> */}
        </div>
      </div>
    </div>
  );
}

export default App;
