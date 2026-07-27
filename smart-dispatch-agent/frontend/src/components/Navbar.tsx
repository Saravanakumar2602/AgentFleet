export const Navbar = () => {
  return (
    <nav className="bg-gradient-to-r from-blue-600 to-indigo-800 text-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <span className="text-3xl" role="img" aria-label="truck">
              🚚
            </span>
            <div>
              <h1 className="text-xl font-bold tracking-wide">Smart Dispatch Agent</h1>
              <p className="text-xs text-blue-200">Demonstration Platform</p>
            </div>
          </div>
          <div className="flex items-center space-x-2 bg-blue-500/20 px-3 py-1.5 rounded-full border border-blue-400/30 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span className="font-semibold tracking-wider uppercase">System Live</span>
          </div>
        </div>
      </div>
    </nav>
  );
};
