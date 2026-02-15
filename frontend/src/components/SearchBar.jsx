function SearchBar({ value, onChange, placeholder = "Search..." }) {
  return (
    <div className="search-bar">
      <span className="search-icon">🔍</span>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="search-input"
      />
      {value && (
        <button 
          className="search-clear"
          onClick={() => onChange('')}
        >
          ×
        </button>
      )}
    </div>
  );
}

export default SearchBar;
