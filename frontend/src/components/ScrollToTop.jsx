import { useEffect } from "react";
import { useLocation } from "react-router-dom";

// React Router does not reset scroll position on navigation by default, so
// switching tabs (e.g. from a long Analysis Result page to Pipeline Flow)
// otherwise lands mid-page instead of at the top.
export default function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}
