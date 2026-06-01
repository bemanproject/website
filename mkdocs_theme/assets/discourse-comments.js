(function () {
  const mount = document.querySelector("#discourse-comments");
  if (!mount) return;

  const forum = mount.dataset.discourseUrl;
  if (!forum || window.location.hostname !== "bemanproject.org") return;

  const discourseUrl = forum.endsWith("/") ? forum : `${forum}/`;
  window.DiscourseEmbed = {
    discourseUrl,
    discourseEmbedUrl: window.location.href,
  };

  const script = document.createElement("script");
  script.async = true;
  script.src = `${discourseUrl}javascripts/embed.js`;
  document.body.appendChild(script);
})();
