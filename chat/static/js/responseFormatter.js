// responseFormatter.js

// Import the marked library for markdown parsing
import { marked } from "https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/lib/marked.esm.min.js";

// Configure marked options
marked.setOptions({
  highlight: function (code, language) {
    return code;
  },
  breaks: true,
  gfm: true,
});

// Custom renderer to handle code blocks and other markdown elements
const renderer = {
  code(code, language) {
    return `<pre class="bg-gray-100 p-3 rounded-lg overflow-x-auto"><code class="language-${language}">${code}</code></pre>`;
  },
  blockquote(quote) {
    return `<blockquote class="border-l-4 border-gray-300 pl-4 my-2 text-gray-600">${quote}</blockquote>`;
  },
  paragraph(text) {
    return `<p class="mb-4">${text}</p>`;
  },
  strong(text) {
    return `<strong class="font-bold">${text}</strong>`;
  },
  em(text) {
    return `<em class="italic">${text}</em>`;
  },
  list(body, ordered) {
    const type = ordered ? "ol" : "ul";
    const className = "list-" + (ordered ? "decimal" : "disc") + " ml-6 mb-4";
    return `<${type} class="${className}">${body}</${type}>`;
  },
  listitem(text) {
    return `<li class="mb-2">${text}</li>`;
  },
};

marked.use({ renderer });

// Function to format the chat message
export function formatMessage(message) {
  try {
    return marked(message);
  } catch (error) {
    console.error("Error formatting message:", error);
    return message; // Return original message if formatting fails
  }
}
