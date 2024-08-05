import React, { useState, useEffect } from 'react';
import { fetchItems } from '../services/api';

const ItemList = () => {
    const [items, setItems] = useState([]);

    useEffect(() => {
        const getItems = async () => {
            try {
                const data = await fetchItems();
                setItems(data);
            } catch (error) {
                console.error('Error fetching items', error);
            }
        };

        getItems();
    }, []);

    return (
        <div>
            <h1>Items</h1>
            <ul>
                {items.map(item => (
                    <li key={item.id}>{item.name}: {item.description}</li>
                ))}
            </ul>
        </div>
    );
};

export default ItemList;
