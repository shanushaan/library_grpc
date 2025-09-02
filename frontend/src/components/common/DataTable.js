import React from 'react';

const DataTable = ({ 
  data, 
  columns, 
  keyField = 'id',
  emptyMessage = 'No data available',
  className = 'data-table'
}) => {
  if (data.length === 0) {
    return <p>{emptyMessage}</p>;
  }

  return (
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
          {data.map(row => (
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
  );
};

export default DataTable;