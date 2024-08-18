import React, { useEffect, useRef, useState } from 'react';
import './App.css';
import gptLogo from './assets/chatgpt1.png';
// import addBtn from './assets/add-30.png';
import sendBtn from './assets/send.svg';
import userIcon from './assets/my-face.jpg';
import gptImgLogo from './assets/chat_bot_icon.jpeg';
import { useSpring, useTrail, animated, config } from '@react-spring/web';
import { saveChatToCache, saveCacheToDb, fetchChatFromDb, fetchChats } from './services/api';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faQuestionCircle } from '@fortawesome/free-solid-svg-icons';
import { htmlToText } from 'html-to-text';


function App() {
  const msgEnd = useRef(null);
  const mapContainer = useRef(null);
  const [input, setInput] = useState("");
  const [option, setOption] = useState("generation");
  const [messages, setMessages] = useState([]);
  const [chatId, setChatId] = useState(null);
  const [previousChats, setPreviousChats] = useState([]);
  const [similarQuestion, setSimilarQuestion] = useState("");
  const [previousResponses, setPreviousResponses] = useState([]);
  const [mappingData, setMappingData] = useState(null);

  useEffect(() => {
    if (msgEnd.current) {
      msgEnd.current.scrollIntoView();
    }
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

  useEffect(() => {
    if (mappingData && mapContainer.current) {
      plotMap(mappingData);
    }
  }, [mappingData]);

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
      const response = await saveChatToCache([userMessage], option);

      console.log('API Response:', response); // Log the full response

      if (option === 'mapping') {
        const generationData = response.data.response_data?.generation_data;
        if (!generationData) {
          throw new Error('No generation data found in response');
        }

        // Convert the markup response to plain text
        let botResponse = htmlToText(generationData.answer, {
          wordwrap: 130
        });

        // Remove everything after "SQL_query"
        const sqlQueryIndex = botResponse.indexOf('SQL_query:');
        if (sqlQueryIndex !== -1) {
          botResponse = botResponse.substring(0, sqlQueryIndex).trim();
        }

        const botMessage = { text: botResponse, isBot: true, option };
        setMessages(prevMessages => [...prevMessages, botMessage]);
        setPreviousResponses(prevResponses => [...prevResponses, botMessage]);

        const mappingData = JSON.parse(response.data.response_data?.mapping_data || '[]');
        if (!Array.isArray(mappingData)) {
          throw new Error('Unexpected mapping data format');
        }
        setMappingData(mappingData);
      } else {
        const chatData = response.chat_data;
        const similarQ = response.similar_question || "";
        setSimilarQuestion(similarQ);

        if (!chatData || !Array.isArray(chatData)) {
          throw new Error('chat_data is missing or not an array');
        }

        const botMessages = chatData.map(msg => {
          let text = htmlToText(msg.text, {
            wordwrap: 130
          });

          // Remove everything after "SQL_query"
          const sqlQueryIndex = text.indexOf('SQL_query:');
          if (sqlQueryIndex !== -1) {
            text = text.substring(0, sqlQueryIndex).trim();
          }

          return { text, isBot: msg.isBot, option };
        });

        setMessages(prevMessages => [...prevMessages, ...botMessages]);
        setPreviousResponses(prevResponses => [...prevResponses, ...botMessages]);
      }
    } catch (error) {
      console.error('Error during chat processing:', error.message, error);

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

  // Function to plot the map using Leaflet.js
  const plotMap = (mappingData) => {
    if (mapContainer.current) {
      // Clear any existing map
      if (mapContainer.current._leaflet_id) {
        mapContainer.current._leaflet_id = null;
        mapContainer.current.innerHTML = '';
      }

      // Create a new map instance
      const map = L.map(mapContainer.current).setView([51.505, -0.09], 13); // Default view

      // Add a tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
      }).addTo(map);

      // Choose a random coordinate from the mapping data to set as the center
      let randomCenter = [51.505, -0.09]; // Default center if mappingData is empty

      if (mappingData.length > 0) {
        const randomIndex = Math.floor(Math.random() * mappingData.length);
        const randomCoordinates = mappingData[randomIndex].coordinates;

        if (randomCoordinates && randomCoordinates.length > 0) {
          randomCenter = [randomCoordinates[0][1], randomCoordinates[0][0]]; // Assuming the first pair of coordinates
        }
      }

      // Set the view of the map to the random center
      map.setView(randomCenter, 13);

      // Add polygons to the map with enhanced styling
      mappingData.forEach((item, index) => {
        try {
          if (item.coordinates && Array.isArray(item.coordinates)) {
            // Extract coordinates for the polygon
            const latLngs = item.coordinates.map(coordPair => {
              if (Array.isArray(coordPair) && coordPair.length === 2) {
                return [coordPair[1], coordPair[0]]; // Convert to [lat, lng]
              } else {
                console.error(`Invalid coordinate format at index ${index}: ${coordPair}`);
                return null; // Return null for invalid coordinates
              }
            }).filter(coord => coord !== null); // Filter out any null coordinates

            // Check if there are valid coordinates to create a polygon
            if (latLngs.length > 0) {
              L.polygon(latLngs, {
                color: '#3388ff', // Border color
                weight: 4, // Border width
                opacity: 0.8, // Border opacity
                fillColor: '#3388ff', // Fill color
                fillOpacity: 0.4 // Fill opacity
              }).addTo(map);
            } else {
              console.error(`No valid coordinates found for polygon at index ${index}`);
            }
          } else {
            console.error(`Missing or invalid coordinates at index ${index}:`, item);
          }
        } catch (error) {
          console.error(`Error processing item at index ${index}:`, error);
        }
      });
    } else {
      console.error('Map container not found');
    }
  };


  // Button hover effect
  const [hovered, setHovered] = useState(false);
  const buttonAnimation = useSpring({
    scale: hovered ? 1.05 : 1,
    config: { tension: 300, friction: 10 },
  });

  // Chat message animation with trail
  const trail = useTrail(previousResponses.length, {
    from: { opacity: 0, transform: 'translate3d(0, 20px, 0)' },
    to: { opacity: 1, transform: 'translate3d(0, 0px, 0)' },
    config: config.gentle,
  });

  // Sidebar slide-in effect
  const sidebarAnimation = useSpring({
    from: { opacity: 0, transform: 'translate3d(-30px, 0, 0)' },
    to: { opacity: 1, transform: 'translate3d(0, 0, 0)' },
  });

  return (
    <div className="App">
      <animated.div className="sidebar" style={sidebarAnimation}>
        <div className="fixedContent">
          <img src={gptLogo} alt='logo' className='logo' />
          <span className='brand'></span>
          <animated.button
            style={buttonAnimation}
            className='midBtn'
            onClick={handleNewChat}
            onMouseEnter={() => setHovered(true)}
            onMouseLeave={() => setHovered(false)}
          >
            New Chat
          </animated.button>
        </div>
        <div className="scrollableContent">
          {previousChats.map((chat) => (
            <animated.button
              key={chat.id}
              style={sidebarAnimation}
              className='query'
              onClick={() => loadPreviousChat(chat.id)}
            >
              Chat {chat.id} - {new Date(chat.created_at).toLocaleString()}
            </animated.button>
          ))}
        </div>
      </animated.div>

      <div className='main'>
        <div className='chats scrollableContent'>
          {trail.map((props, i) =>
            <animated.div key={i} style={props} className={previousResponses[i].isBot ? 'chat bot' : 'chat user'}>
              <img className='chatImg' src={previousResponses[i].isBot ? gptImgLogo : userIcon} alt='' />
              <p className='txt'>{previousResponses[i].text}</p>
            </animated.div>
          )}
          <div ref={msgEnd}></div>
        </div>
        {option === 'mapping' && (
          <div
            className="mapContainer"
            ref={mapContainer}
            style={{ height: '500px', width: '100%' }}
          ></div>
        )}

        <div className='chatFooter'>
          {similarQuestion && (
            <div className='similarQuestionBox' onClick={() => setInput(similarQuestion)}>
              <FontAwesomeIcon icon={faQuestionCircle} className='similarQuestionIcon' />
              <span className='similarQuestionText'>Did you mean: <strong>{similarQuestion}</strong></span>
            </div>
          )}
          <div className='inp'>
            <select value={option} onChange={(e) => setOption(e.target.value)}>
              <option value="generation">Generation</option>
              <option value="retrieval">Retrieval</option>
              <option value="comparative">Comparative</option>
              <option value="mapping">Mapping</option>
            </select>
            <input
              type='text'
              placeholder='Send a message'
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleEnter}
            />
            <button className='send' onClick={handleSend}><img src={sendBtn} alt='send' /></button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
