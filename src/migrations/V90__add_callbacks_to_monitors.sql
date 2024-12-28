ALTER TABLE monitor
ADD COLUMN callbacks JSONB DEFAULT '[]'::jsonb;
