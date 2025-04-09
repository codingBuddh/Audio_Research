import {
  VStack,
  Heading,
  Text,
  Box,
  Badge,
} from '@chakra-ui/react'
import { Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon } from '@chakra-ui/accordion'
import { AudioAnalysisResponse, ChunkStatus } from '../types'

interface AnalysisResultsProps {
  results: AudioAnalysisResponse
}

export const AnalysisResults = ({ results }: AnalysisResultsProps) => {
  const getStatusColor = (status: ChunkStatus) => {
    switch (status) {
      case ChunkStatus.COMPLETED:
        return 'green'
      case ChunkStatus.PROCESSING:
        return 'blue'
      case ChunkStatus.FAILED:
        return 'red'
      default:
        return 'gray'
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <Box>
      <Heading size="md" mb={4}>Analysis Results</Heading>
      
      <Accordion allowMultiple>
        {results.chunks.map((chunk) => (
          <AccordionItem key={chunk.chunk_id} value={chunk.chunk_id.toString()}>
            <h2>
              <AccordionButton>
                <Box flex="1" textAlign="left">
                  <Text fontWeight="medium">
                    Chunk {chunk.chunk_id + 1} ({formatTime(chunk.start_time)} - {formatTime(chunk.end_time)})
                  </Text>
                </Box>
                <Badge colorScheme={getStatusColor(chunk.status)} mr={2}>
                  {chunk.status}
                </Badge>
                <AccordionIcon />
              </AccordionButton>
            </h2>
            
            <AccordionPanel pb={4}>
              {chunk.status === ChunkStatus.COMPLETED && chunk.features ? (
                <Box>
                  {chunk.features.mfcc && (
                    <Box mb={3}>
                      <Text fontWeight="bold">MFCCs:</Text>
                      <Text fontSize="sm" color="gray.600">
                        {chunk.features.mfcc.map((v: number) => v.toFixed(2)).join(', ')}
                      </Text>
                    </Box>
                  )}
                  
                  {chunk.features.pitch && (
                    <Box mb={3}>
                      <Text fontWeight="bold">Pitch:</Text>
                      <Text fontSize="sm" color="gray.600">
                        {chunk.features.pitch.toFixed(2)} Hz
                      </Text>
                    </Box>
                  )}
                  
                  {chunk.features.emotion_scores && (
                    <Box mb={3}>
                      <Text fontWeight="bold">Emotion Scores:</Text>
                      <Text fontSize="sm" color="gray.600">
                        Arousal: {chunk.features.emotion_scores.arousal.toFixed(2)},
                        Valence: {chunk.features.emotion_scores.valence.toFixed(2)}
                      </Text>
                    </Box>
                  )}
                  
                  {chunk.features.speaking_rate && (
                    <Box mb={3}>
                      <Text fontWeight="bold">Speaking Rate:</Text>
                      <Text fontSize="sm" color="gray.600">
                        {chunk.features.speaking_rate.toFixed(2)} syllables/second
                      </Text>
                    </Box>
                  )}
                </Box>
              ) : chunk.status === ChunkStatus.FAILED ? (
                <Text color="red.500">{chunk.error}</Text>
              ) : (
                <Text color="gray.500">Processing...</Text>
              )}
            </AccordionPanel>
          </AccordionItem>
        ))}
      </Accordion>
    </Box>
  )
}