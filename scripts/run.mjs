import {spawn} from 'node:child_process';
import {existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname,resolve} from 'node:path';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const mode=process.argv[2]||'dev',dev=mode==='dev',children=[];
const python=process.env.PYTHON_BIN||(existsSync(resolve(root,'.venv/bin/python'))?resolve(root,'.venv/bin/python'):'python3');
let stopping=false;
function stop(code=0){if(stopping)return;stopping=true;process.exitCode=code;for(const child of children)child.kill('SIGTERM');setTimeout(()=>{for(const child of children)child.kill('SIGKILL');process.exit(code);},2000).unref();}
function start(command,args,env={},cwd=root){const child=spawn(command,args,{cwd,env:{...process.env,...env},stdio:'inherit'});children.push(child);child.on('error',err=>{console.error(`Could not launch ${command}: ${err.message}`);stop(1);});child.on('exit',code=>{if(!stopping)stop(code||0);});return child;}
start(python,['-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8000',...(dev?['--reload','--reload-dir','backend']:[])],{PYTHONUNBUFFERED:'1'});
const backend='http://127.0.0.1:8000/api/health';
let healthy=false;
for(let i=0;i<80&&!stopping;i++){try{const r=await fetch(backend);if(r.ok){healthy=true;break;}}catch{}await new Promise(r=>setTimeout(r,250));}
if(!healthy){console.error('Backend did not become healthy. Check Python dependencies.');stop(1);}else{
 const standalone=process.env.STANDALONE_SERVER;
 if(!dev&&standalone)start(process.execPath,[standalone],{HOSTNAME:'0.0.0.0',PORT:process.env.PORT||'3000',NODE_ENV:'production'},dirname(standalone));
 else start(process.execPath,[resolve(root,'node_modules/next/dist/bin/next'),dev?'dev':'start',...(dev?['--webpack']:[]),'-H','0.0.0.0','-p',process.env.PORT||'3000'],{NEXT_TELEMETRY_DISABLED:'1'});
}
process.on('SIGINT',()=>stop());process.on('SIGTERM',()=>stop());
