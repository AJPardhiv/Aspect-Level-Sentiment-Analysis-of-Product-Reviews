import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import eventRoutes from './routes/eventRoutes.js';
import workflowRoutes from './routes/workflowRoutes.js';
import chatRoutes from './routes/chatRoutes.js';

dotenv.config();

const app = express();

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true,
}));
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'OK', timestamp: new Date() });
});

// Routes
app.use('/api/events', eventRoutes);
app.use('/api/workflow', workflowRoutes);
app.use('/api/chat', chatRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong',
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 MetisFlow API running on port ${PORT}`);
});

export default app;
