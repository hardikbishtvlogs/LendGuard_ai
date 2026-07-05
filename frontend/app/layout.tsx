import "./globals.css"; import {Nav} from "@/components/Nav"; import {Footer} from "@/components/Footer";
export const metadata={title:"LendGuard AI",description:"Enterprise loan risk intelligence"};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body><Nav/>{children}<Footer/></body></html>}
