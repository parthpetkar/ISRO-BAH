import './App.css';
import gptLogo from './assets/chatgpt.svg';
import addBtn from './assets/add-30.png';
import msgIcon from './assets/message.svg';
import home from './assets/home.svg';
import saved from './assets/bookmark.svg';
import rocket from './assets/rocket.svg';
import sendBtn from './assets/send.svg';
import userIcon from './assets/user-icon.png';
import gptImgLogo from './assets/chatgptLogo.svg';
import { useEffect, useRef, useState } from 'react';

function App() {

  const msgEnd = useRef(null);

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    {
      text: "hi i am djangogpt",
      isBot: true
    }
  ]);

  useEffect(()=>{
    msgEnd.current.scrollIntoView();
  }, [messages])

  const sendMsg = async (text) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/sample-data/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: text }),
      });
      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error('Error sending message:', error);
      return 'Error: could not get response from server';
    }
  };

  const handleSend = async () => {
    const text = input;
    setInput('');
    setMessages(prevMessages => [
      ...prevMessages,
      { text, isBot: false }
    ]);
    const res = await sendMsg(text);
    setMessages(prevMessages => [
      ...prevMessages,
      {
        text: res,
        isBot: true
      }
    ]);
  };

  const handleEnter = async (e) => {
    if (e.key === 'Enter') await handleSend();
  };

  return (
    <div className="App">
      <div className="sidebar">
        <div className="upperSide">
          <div className="upperSideTop">
            <img src={gptLogo} alt='logo' className='logo' /><span className='brand'></span>
            <button className='midBtn' onClick={() => { window.location.reload() }}><img src={addBtn} alt='new chat' className='addBtn' />New Chat</button>
            <div className='upperSideBottom'>
              <button className='query'><img src={msgIcon} alt='query' />What is Programming</button>
              <button className='query'><img src={msgIcon} alt='query' />How to use an API</button>
            </div>
          </div>
        </div>
        <div className="lowerSide">
          <div className='listItems'><img src={home} alt='' className='listItemsImg' />Home</div>
          <div className='listItems'><img src={saved} alt='' className='listItemsImg' />Saved</div>
          <div className='listItems'><img src={rocket} alt='' className='listItemsImg' />Upgrade</div>
        </div>
      </div>

      <div className='main'>
        <div className='chats'>
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
          <p>Chat may produce incorrect results</p>
        </div>
      </div>
    </div>
  );
}

export default App;
