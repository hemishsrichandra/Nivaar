'use client';
import {useState,useRef,useEffect} from 'react';
import {Menu,X,type LucideIcon} from 'lucide-react';
export function ProductNavigation({items,active,count,onNavigate}:{items:{id:string;label:string;icon:LucideIcon}[];active:string;count:number;onNavigate:(id:string)=>void}){
 const [open,setOpen]=useState(false),ref=useRef<HTMLDivElement>(null),trigger=useRef<HTMLButtonElement>(null);
 useEffect(()=>{if(!open)return;const outside=(e:PointerEvent)=>{if(!ref.current?.contains(e.target as Node))setOpen(false);};const escape=(e:KeyboardEvent)=>{if(e.key==='Escape'){setOpen(false);trigger.current?.focus();}};document.addEventListener('pointerdown',outside);document.addEventListener('keydown',escape);return()=>{document.removeEventListener('pointerdown',outside);document.removeEventListener('keydown',escape);};},[open]);
 return <div className="product-navigation" ref={ref}><button ref={trigger} className="menu-trigger" aria-expanded={open} aria-controls="product-menu" aria-label={open?'Close menu':'Open menu'} onClick={()=>setOpen(!open)}>{open?<X size={21}/>:<Menu size={21}/>}</button><nav id="product-menu" className={open?'menu-open':''} aria-label="Main navigation">{items.map(n=><button key={n.id} className={'nav-item '+(active===n.id?'active':'')} aria-current={active===n.id?'page':undefined} onClick={()=>{setOpen(false);onNavigate(n.id);}}><n.icon size={17}/><span>{n.label}</span>{n.id==='history'&&count>0&&<span className="count" aria-label={`${count} recent checks`}>{count}</span>}</button>)}</nav></div>;
}
