const YouTubeTransformer = {
  name: "YouTube",
  shouldTransform(url) {
    try {
      const parsed = new URL(url);
      const hostname = parsed.hostname.toLowerCase();
      const allowedHosts = [
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be"
      ];
      return allowedHosts.includes(hostname);
    } catch (e) {
      // If the URL cannot be parsed, it cannot be a valid YouTube URL.
      return false;
    }
  },
  getHTML(url) {
    const urlObj = new URL(url);
    const isShort = urlObj.hostname.toLowerCase() === "youtu.be" || urlObj.hostname.toLowerCase() === "www.youtu.be";
    const videoId = isShort
      ? urlObj.pathname.split("/").filter(Boolean).pop()
      : urlObj.searchParams.get("v");

    return `
      <iframe
        src="https://www.youtube.com/embed/${videoId}"
        style="width:100%; aspect-ratio:16/9; border:0;"
        allowfullscreen
      ></iframe>
    `;
  },
};

module.exports = YouTubeTransformer;
