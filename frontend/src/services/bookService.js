import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const bookService = {
  async getBooks() {
    const response = await axios.get(API_CONFIG.getVersionedUrl('/admin/books'));
    return response.data;
  },

  async createBook(bookData) {
    const response = await axios.post(API_CONFIG.getVersionedUrl('/admin/books'), bookData);
    return response.data;
  },

  async updateBook(bookId, bookData) {
    const response = await axios.put(API_CONFIG.getVersionedUrl(`/admin/books/${bookId}`), bookData);
    return response.data;
  },

  async deleteBook(bookId) {
    const response = await axios.delete(API_CONFIG.getVersionedUrl(`/admin/books/${bookId}`));
    return response.data;
  },

  async searchBooks(query) {
    const response = await axios.get(API_CONFIG.getVersionedUrl(`/books/search?q=${encodeURIComponent(query)}`));
    return response.data;
  }
};