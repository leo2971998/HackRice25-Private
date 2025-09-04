import { Link, NavLink } from "react-router-dom";

export default function Navbar() {
  return (
	<nav className="sticky top-0 z-10 backdrop-blur supports-[backdrop-filter]:bg-white/70 dark:supports-[backdrop-filter]:bg-neutral-950/70 border-b border-neutral-200 dark:border-neutral-800">
	  <div className="mx-auto max-w-4xl px-4 h-14 flex items-center justify-between">
	    <Link to="/" className="font-semibold">Houston Financial Navigator</Link>
	    <div className="flex items-center gap-4 text-sm">
	      <NavLink to="/" className={({isActive})=> isActive?"underline":undefined}>Chat</NavLink>
	      <NavLink to="/learn" className={({isActive})=> isActive?"underline":undefined}>Learn</NavLink>
	    </div>
	  </div>
	</nav>
  );
}