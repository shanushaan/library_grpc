import React, { useState, useEffect } from 'react';
import { Search, UserCheck, UserX, Edit, Plus, X } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUsers, createUser, updateUser, toggleUserStatus } from '../../store/slices/usersSlice';
import { showNotification } from '../../store/slices/uiSlice';
import EnhancedDataTable from '../common/EnhancedDataTable';
import '../../styles/UsersManagement.css';
import '../../styles/Modal.css';

const UsersManagement = () => {
  const dispatch = useDispatch();
  const { data: users, loading } = useSelector(state => state.users);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'USER',
    is_active: true
  });



  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);



  // Handle create/update user
  const handleSaveUser = async (e) => {
    e.preventDefault();
    try {
      const payload = { ...formData };
      if (editingUser && !payload.password) {
        delete payload.password;
      }
      
      if (editingUser) {
        await dispatch(updateUser({ userId: editingUser.user_id, userData: payload })).unwrap();
      } else {
        await dispatch(createUser(payload)).unwrap();
      }
      
      dispatch(fetchUsers());
      dispatch(showNotification({ message: 'User saved successfully', type: 'success' }));
      handleCloseModal();
    } catch (error) {
      dispatch(showNotification({ message: 'Error saving user', type: 'error' }));
    }
  };

  // Handle toggle user status
  const handleToggleStatus = async (userId, currentStatus) => {
    const user = users.find(u => u.user_id === userId);
    const action = currentStatus ? 'deactivate' : 'activate';
    const confirmed = window.confirm(`Are you sure you want to ${action} user "${user.username}"?`);
    
    if (!confirmed) return;
    
    try {
      await dispatch(toggleUserStatus(userId)).unwrap();
      dispatch(showNotification({ message: `User ${action}d successfully`, type: 'success' }));
    } catch (error) {
      dispatch(showNotification({ message: 'Error updating user status', type: 'error' }));
    }
  };

  // Handle edit user
  const handleEditUser = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username || '',
      email: user.email || '',
      password: '', // Don't pre-fill password
      role: user.role || 'USER',
      is_active: user.is_active
    });
    setShowModal(true);
  };

  // Handle add new user
  const handleAddUser = () => {
    setEditingUser(null);
    setFormData({
      username: '',
      email: '',
      password: '',
      role: 'USER',
      is_active: true
    });
    setShowModal(true);
  };

  // Handle close modal
  const handleCloseModal = () => {
    setShowModal(false);
    setEditingUser(null);
    setFormData({
      username: '',
      email: '',
      password: '',
      role: 'USER',
      is_active: true
    });
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <div className="header-left">
          <h2>Library Users & Members Management</h2>
          <p>Manage library users and members ({users.length} users)</p>
        </div>

      </div>
      


      {loading ? (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading users...</p>
        </div>
      ) : (
        <EnhancedDataTable
          data={users}
          columns={[
            { key: 'username', header: 'Username' },
            { key: 'email', header: 'Email' },
            { 
              key: 'role', 
              header: 'Role',
              render: (value) => (
                <span className={`role-badge ${value.toLowerCase()}`}>
                  {value}
                </span>
              )
            },
            { 
              key: 'is_active', 
              header: 'Status',
              render: (value) => (
                <span className={`status-badge ${value ? 'active' : 'inactive'}`}>
                  {value ? (
                    <>
                      <UserCheck size={14} />
                      Active
                    </>
                  ) : (
                    <>
                      <UserX size={14} />
                      Inactive
                    </>
                  )}
                </span>
              )
            },
            {
              key: 'actions',
              header: 'Actions',
              render: (_, user) => (
                <div className="table-actions">
                  <button className="action-btn edit" title="Edit User" onClick={() => handleEditUser(user)}>
                    <Edit size={14} />
                  </button>
                  <button 
                    className={`action-btn ${user.is_active ? 'deactivate' : 'activate'}`}
                    title={user.is_active ? 'Deactivate' : 'Activate'}
                    onClick={() => handleToggleStatus(user.user_id, user.is_active)}
                  >
                    {user.is_active ? <UserX size={14} /> : <UserCheck size={14} />}
                  </button>
                </div>
              )
            }
          ]}
          keyField="user_id"
          emptyMessage="No users found"
          className="users-table"
          searchable={true}
          searchPlaceholder="Search users..."
          filters={[
            { value: 'USER', label: 'Users', filter: (user) => user.role === 'USER' },
            { value: 'ADMIN', label: 'Admins', filter: (user) => user.role === 'ADMIN' },
            { value: 'ACTIVE', label: 'Active Only', filter: (user) => user.is_active },
            { value: 'INACTIVE', label: 'Inactive Only', filter: (user) => !user.is_active }
          ]}
          actions={
            <button className="btn primary" onClick={handleAddUser}>
              <Plus size={20} />
              Add New User
            </button>
          }
        />
      )}

      {!loading && filteredUsers.length === 0 && (
        <div className="no-results">
          <UserCheck size={48} />
          <h3>No users found</h3>
          <p>Try adjusting your search terms or filters</p>
        </div>
      )}

      {/* User Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{editingUser ? 'Edit User' : 'Add New User'}</h3>
              <button className="close-btn" onClick={handleCloseModal}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSaveUser}>
              <div className="form-group">
                <label>Username *</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Password {editingUser ? '(leave empty to keep current)' : '*'}</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required={!editingUser}
                />
              </div>
              <div className="form-group">
                <label>Role *</label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  required
                >
                  <option value="USER">User</option>
                  <option value="ADMIN">Admin</option>
                </select>
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                  />
                  Active User
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn secondary" onClick={handleCloseModal}>
                  Cancel
                </button>
                <button type="submit" className="btn primary" disabled={loading}>
                  {loading ? 'Saving...' : (editingUser ? 'Update' : 'Create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersManagement;