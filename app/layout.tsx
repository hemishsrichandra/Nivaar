import type {Metadata} from 'next';
import './globals.css';
export const metadata:Metadata={title:'Nivaar — Pause. Check. Stay protected.',description:'Verify suspicious messages and links against official Indian government evidence. A private, evidence-first workspace.',icons:{icon:'/favicon.svg'}};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>;}
