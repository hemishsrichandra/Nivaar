import {parseInput} from '../../../lib/server/request';
import {investigate} from '../../../lib/server/investigation-agent';
import {evidencePdf} from '../../../lib/server/evidence-pdf';
// Regenerate from validated intake, never trust a client-supplied verdict.
export async function POST(request:Request){try{const report=await investigate(await parseInput(request));return new Response(evidencePdf(report),{headers:{'Content-Type':'application/pdf','Content-Disposition':'attachment; filename="nivaar-evidence.pdf"','Cache-Control':'no-store'}});}catch{return Response.json({error:'Could not create the report. Check your input and try again.'},{status:400});}}
