function res = query(result_dir, filter, process)
% Returns the results matching a metadata filter.
%    
% Parameters
% ----------
% result_dir : str
%   Directory containing the results and metadata file.
% filter : str, optional
%   A string containing command-line options and arguments used to filter the
%   result set. See `erun -h` for details.
% process : function, optional
%   A function to load and process each data file. If provided, this
%   function will be called once for each result file (given the
%   path to the file as input), and its return value placed into
%   the `res` field of the returned struct.
%
% Returns
% -------
% results : struct
if nargin < 2
    filter = '';
end

[status, output] = system(['equery -o ' result_dir ' ' filter]);

header = textscan(output, '%s', 1, 'delimiter', '');
cols = regexp(header{1}{1}, '\t', 'split');
ncol = length(cols);
table = textscan(output, repmat('%s ',1,ncol), 'Headerlines', 1);

res = cell2struct(table, cols, 2);
if nargin >= 3
    res.res = cellfun(process, res.outfile);
end
