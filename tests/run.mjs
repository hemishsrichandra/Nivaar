import {build} from 'esbuild';
import {mkdtemp,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
const dir=await mkdtemp(join(tmpdir(),'nivaar-tests-'));
try{const out=join(dir,'checks.mjs');await build({entryPoints:['tests/checks.ts'],outfile:out,bundle:true,platform:'node',format:'esm',logLevel:'error'});await import(pathToFileURL(out).href);}finally{await rm(dir,{recursive:true,force:true});}
