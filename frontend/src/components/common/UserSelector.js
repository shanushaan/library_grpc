import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';

const UserSelector = ({ onUserSelect, selectedUser }) => {
  const [users, setUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const userData = await adminService.fetchUsers();
        setUsers(userData);
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    };
    fetchUsers();
  }, []);

  const filteredUsers = users.filter(user => 
    user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div>
      <div className="form-group">
        <label>Search Users</label>
        <input
          type="text"
          placeholder="Search by username or email..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>
      <div className="users-list">
        {filteredUsers.map(user => (
          <div 
            key={user.user_id} 
            className={`user-item ${selectedUser?.user_id === user.user_id ? 'selected' : ''}`}
            onClick={() => onUserSelect(user)}
          >
            <div className="user-info">
              <strong>{user.username}</strong>
              <span>{user.email}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UserSelector;