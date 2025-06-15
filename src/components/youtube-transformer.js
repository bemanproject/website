const YouTubeTransformer = {
  name: 'YouTube',
  shouldTransform(url) {
    return url.includes('youtube.com') || url.includes('youtu.be');
  },
  getHTML(url) {
    const videoId = url.includes('youtu.be')
      ? url.split('/').pop()
      : new URL(url).searchParams.get('v');

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
