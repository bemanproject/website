import React, { useState } from 'react';
import Modal from 'react-modal';

// Bind modal to app element for accessibility
Modal.setAppElement('#__docusaurus');

export default function Godbolt({ url }) {
  const [isOpen, setIsOpen] = useState(false);

  const getHTMLIframe = (url) => {
    if (!url.includes('godbolt.org')) {
      return '<p>Invalid Godbolt URL</p>';
    }
    const fullUrl = url.trim().includes('godbolt.org/#')
      ? url.replace('godbolt.org/#', 'godbolt.org/e?hideEditorToolbars=false#')
      : url;
    return `<iframe src="${fullUrl}" style="margin:auto; width:100%; height:100%; display:block; overflow:hidden;" frameBorder="0"></iframe>`;
  };

  const openModal = () => setIsOpen(true);
  const closeModal = () => setIsOpen(false);
  const iframeHTML = getHTMLIframe(url);

  return (
    <div>
      <a
        href={url}
        onClick={(e) => {
          e.preventDefault();
          openModal();
        }}
        style={{
          fontSize: '16px',
          color: '#007bff',
          textDecoration: 'underline',
          cursor: 'pointer',
          zIndex: 1000,
        }}
        onMouseOver={(e) => (e.target.style.color = '#0056b3')}
        onMouseOut={(e) => (e.target.style.color = '#007bff')}
      >
        Try it on Compiler Explorer 🚀
      </a>
      <Modal
        isOpen={isOpen}
        onRequestClose={closeModal}
        style={{
          content: {
            top: '50%',
            left: '50%',
            right: 'auto',
            bottom: 'auto',
            marginRight: '-50%',
            transform: 'translate(-50%, -50%)',
            width: '90%',
            height: '90%',
            padding: 0,
          },
          overlay: { zIndex: 1001 },
        }}
        contentLabel="Godbolt Compiler Modal"
      >
        <div
          style={{ width: '100%', height: '100%' }}
          dangerouslySetInnerHTML={{ __html: iframeHTML }}
        />
        <button
          onClick={closeModal}
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            padding: '5px 10px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
          }}
        >
          Close
        </button>
      </Modal>
    </div>
  );
}