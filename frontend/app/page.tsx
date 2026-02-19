"use client";

import { useEffect, useState } from "react";

type Book = {
  title: string;
  authors?: string;
  similarity?: number;
  thumbnail?: string;
  preview_link?: string;
};

export default function Home() {
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedBook, setSelectedBook] = useState("");
  const [results, setResults] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchBooks = async () => {
      const res = await fetch("https://book-recommendation-system-0h3h.onrender.com/books");
      const data = await res.json();
      setBooks(data);
    };
    fetchBooks();
  }, []);

  const fetchRecommendations = async () => {
    if (!selectedBook) return;

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const res = await fetch(
        `https://book-recommendation-system-0h3h.onrender.com/query=${encodeURIComponent(
          selectedBook
        )}`
      );

      const data = await res.json();

      if (data.error) {
        setError(data.error);
      } else {
        setResults(data);
      }
    } catch {
      setError("Something went wrong.");
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white">

      {/* HERO */}
      <div className="text-center pt-20 pb-12">
        <h1 className="text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-purple-400 to-indigo-500 bg-clip-text text-transparent">
          Discover Books You’ll Love
        </h1>
        <p className="text-gray-400 mt-4 text-lg">
          Get personalized book recommendations based on your favorite reads.
        </p>
      </div>

      {/* SEARCH PANEL */}
      <div className="max-w-3xl mx-auto px-6">
        <div className="bg-white/5 backdrop-blur-xl p-8 rounded-3xl border border-white/10 shadow-2xl">
          <input
            list="book-list"
            placeholder="Search and select a book..."
            className="w-full p-4 rounded-xl bg-black/40 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500 text-white placeholder-gray-400"
            value={selectedBook}
            onChange={(e) => setSelectedBook(e.target.value)}
          />

          <datalist id="book-list">
            {books.map((book, index) => (
              <option key={index} value={book.title} />
            ))}
          </datalist>

          <button
            onClick={fetchRecommendations}
            className="mt-6 w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:scale-[1.02] hover:shadow-purple-500/40 hover:shadow-lg transition-all duration-300 text-white py-3 rounded-xl font-semibold"
          >
            Get Recommendations
          </button>
        </div>
      </div>

      {/* LOADING */}
      {loading && (
        <div className="text-center mt-10 text-purple-400 animate-pulse">
          Finding the perfect books for you...
        </div>
      )}

      {/* ERROR */}
      {error && (
        <div className="text-center mt-10 text-red-400 font-medium">
          {error}
        </div>
      )}

      {/* RESULTS */}
      <div className="max-w-7xl mx-auto px-6 mt-16 pb-24">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-10">
          {results.map((book, index) => (
            <div
              key={index}
              className="group bg-gradient-to-b from-gray-800 to-gray-900 rounded-3xl overflow-hidden shadow-xl hover:shadow-purple-500/20 hover:-translate-y-2 transition-all duration-500"
            >
              {/* IMAGE */}
              {book.thumbnail ? (
                <a
                  href={book.preview_link}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <div className="overflow-hidden">
                    <img
                      src={book.thumbnail}
                      alt={book.title}
                      className="w-full h-64 object-cover group-hover:scale-110 transition-transform duration-700"
                    />
                  </div>
                </a>
              ) : (
                <div className="w-full h-64 bg-gray-700 flex items-center justify-center text-gray-400">
                  No Image
                </div>
              )}

              {/* CONTENT */}
              <div className="p-5">
                <h2 className="font-bold text-lg line-clamp-2 text-white">
                  {book.title}
                </h2>

                {book.authors && (
                  <p className="text-sm text-gray-400 mt-1">
                    {book.authors}
                  </p>
                )}

                {book.similarity !== undefined && (
                  <p className="text-xs text-purple-400 mt-2">
                    Similarity: {book.similarity.toFixed(3)}
                  </p>
                )}

                {book.preview_link && (
                  <a
                    href={book.preview_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block mt-4 text-center bg-purple-600 hover:bg-purple-700 py-2 rounded-lg text-sm font-medium transition"
                  >
                    View Preview
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* FOOTER */}
      <div className="text-center text-gray-600 pb-6 text-sm">
        &copy; {new Date().getFullYear()} Book Recommendation System. All rights
      </div>
    </div>
  );
}
