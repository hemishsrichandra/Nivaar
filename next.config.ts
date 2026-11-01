import type {NextConfig} from 'next';
const nextConfig:NextConfig={
 output:'standalone',
 poweredByHeader:false,
 experimental:{proxyTimeout:180000},
 async rewrites(){return [{source:'/api/:path*',destination:'http://127.0.0.1:8000/api/:path*'}];},
 async headers(){return [{source:'/:path*',headers:[{key:'X-Content-Type-Options',value:'nosniff'},{key:'Referrer-Policy',value:'strict-origin-when-cross-origin'},{key:'X-Frame-Options',value:'DENY'}]}];}
};
export default nextConfig;
