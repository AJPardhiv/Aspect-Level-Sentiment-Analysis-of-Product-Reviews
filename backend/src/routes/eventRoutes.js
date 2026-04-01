import express from 'express';
import * as eventController from '../controllers/eventController.js';

const router = express.Router();

router.post('/', eventController.submitEvent);
router.get('/', eventController.listEvents);
router.get('/:eventId', eventController.getEvent);

export default router;
