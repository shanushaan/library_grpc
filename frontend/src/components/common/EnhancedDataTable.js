import React, { useState } from 'react';
import { Search } from 'lucide-react';

const EnhancedDataTable = ({ 
  data, 
  columns, 
  keyField = 'id',
  emptyMessage = 'No data available',
  className = 'data-table',
  searchable = false,
  searchPlaceholder = 'Search...',
  filters = [],
  actions = null
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('');

  const filteredData = data.filter(row => {
    const matchesSearch = !searchable || !searchQuery || 
      columns.some(col => 
        String(row[col.key] || '').toLowerCase().includes(searchQuery.toLowerCase())
      );
    
    const matchesFilter = !selectedFilter || 
      filters.find(f => f.value === selectedFilter)?.filter(row) !== false;
    
    return matchesSearch && matchesFilter;
  });

  return (
    <div className={`${className}-wrapper`}>
      {(searchable || filters.length > 0 || actions) && (
        <div className="table-controls">
          {searchable && (
            <div className="search-box">
              <Search size={20} />
              <input
                type="text"
                placeholder={searchPlaceholder}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          )}
          
          {filters.length > 0 && (
            <select 
              value={selectedFilter} 
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">All</option>
              {filters.map(filter => (
                <option key={filter.value} value={filter.value}>
                  {filter.label}
                </option>
              ))}
            </select>
          )}
          
          {actions && <div className="table-actions">{actions}</div>}
        </div>
      )}

      {filteredData.length === 0 ? (
        <div>{emptyMessage}</div>
      ) : (
        <div className={`${className}-container`}>
          <table className={className}>
            <thead>
              <tr>
                {columns.map(column => (
                  <th key={column.key}>{column.header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredData.map(row => (
                <tr key={row[keyField]}>
                  {columns.map(column => (
                    <td key={column.key}>
                      {column.render ? column.render(row[column.key], row) : row[column.key]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default EnhancedDataTable;