#!/bin/bash
echo ""
echo "  ██╗     ███████╗███╗   ██╗███████╗ █████╗ ██╗"
echo "  ██║     ██╔════╝████╗  ██║██╔════╝██╔══██╗██║"
echo "  ██║     █████╗  ██╔██╗ ██║███████╗███████║██║"
echo "  ██║     ██╔══╝  ██║╚██╗██║╚════██║██╔══██║██║"
echo "  ███████╗███████╗██║ ╚████║███████║██║  ██║██║"
echo "  ╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝"
echo ""
echo "  FPV Camera Advisor — starting server..."
echo ""
node server.js &
sleep 1
echo "  Opening http://localhost:3000 ..."
echo ""
# Try to open browser on different platforms
if command -v open &> /dev/null; then
  open http://localhost:3000
elif command -v xdg-open &> /dev/null; then
  xdg-open http://localhost:3000
elif command -v start &> /dev/null; then
  start http://localhost:3000
fi
echo "  If browser didn't open, go to: http://localhost:3000"
echo "  Press Ctrl+C to stop."
echo ""
wait
