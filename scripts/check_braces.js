const fs = require('fs');
let code = fs.readFileSync('frontend/src/pages/Battle.jsx','utf8');
// remove single/double/backtick strings
code = code.replace(/\\\\/g,'\\\\\\').replace(/('(?:[^'\\\\]|\\\\.)*')|("(?:[^"\\\\]|\\\\.)*")|(`(?:[^`\\\\]|\\\\.)*`)/g, '"S"');
let open = 0;
const lines = code.split('\n');
for(let i=0;i<lines.length;i++){
  const line = lines[i];
  for(let j=0;j<line.length;j++){
    const ch = line[j];
    if(ch==='{') open++;
    else if(ch==='}') open--;
    if(open<0){
      console.log('Close without open at line', i+1);
      process.exit(1);
    }
  }
}
if(open!==0) console.log('Brace mismatch, final open count', open);
else console.log('Braces balanced');
