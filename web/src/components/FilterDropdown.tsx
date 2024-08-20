import React from "react";

interface FilterDropdownProps {
  selectedFilter: string;
  onFilterChange: (filter: string) => void;
}

const FilterDropdown: React.FC<FilterDropdownProps> = ({
  selectedFilter,
  onFilterChange,
}) => {
  return (
    <div className="relative">
      <select
        value={selectedFilter}
        onChange={(e) => onFilterChange(e.target.value)}
        className="block appearance-none w-full bg-[#151C32] border border-gray-500 text-white px-4 py-3 pr-8 rounded leading-tight focus:outline-none focus:ring-2 focus:ring-[#41D0C8]"
      >
        <option value="">Select Filter</option>
        <option value="mostRecent">Most Recent Publish Year</option>
        <option value="earliest">Earliest Publish Year</option>
        <option value="topRated">Top Rated</option>
        <option value="leastRated">Least Rated</option>
      </select>
    </div>
  );
};

export default FilterDropdown;
