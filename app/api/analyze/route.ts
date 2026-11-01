import {parseInput} from '../../../lib/server/request';
import {investigate} from '../../../lib/server/investigation-agent';
export async function POST(request:Request){try{return Response.json(await investigate(await parseInput(request)),{headers:{'Cache-Control':'no-store'}});}catch(e){return Response.json({error:e instanceof Error?e.message:'Invalid request'},{status:400});}}
