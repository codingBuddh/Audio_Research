import {
  VStack,
  Heading,
  Text,
  Box,
  Badge,
  SimpleGrid,
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
              {chunk.status === ChunkStatus.COMPLETED && chunk.features?.acoustic ? (
                <SimpleGrid columns={[1, 2]} spacing={4}>
                  {/* MFCCs */}
                  <Box mb={3}>
                    <Text fontWeight="bold">MFCCs:</Text>
                    <Text fontSize="sm" color="gray.600">
                      {chunk.features.acoustic.mfcc.map((v: number) => v.toFixed(2)).join(', ')}
                    </Text>
                  </Box>
                  
                  {/* Pitch */}
                  <Box mb={3}>
                    <Text fontWeight="bold">Pitch:</Text>
                    <Text fontSize="sm" color="gray.600">
                      {chunk.features.acoustic.pitch.toFixed(2)} Hz
                    </Text>
                  </Box>
                  
                  {/* Formants */}
                  <Box mb={3}>
                    <Text fontWeight="bold">Formants:</Text>
                    <Text fontSize="sm" color="gray.600">
                      {chunk.features.acoustic.formants.map((f: number, i: number) => 
                        `F${i+1}: ${f.toFixed(2)} Hz`
                      ).join(', ')}
                    </Text>
                  </Box>
                  
                  {/* Energy */}
                  <Box mb={3}>
                    <Text fontWeight="bold">Energy:</Text>
                    <Text fontSize="sm" color="gray.600">
                      {chunk.features.acoustic.energy.toFixed(4)}
                    </Text>
                  </Box>
                  
                  {/* Zero-Crossing Rate */}
                  <Box mb={3}>
                    <Text fontWeight="bold">Zero-Crossing Rate:</Text>
                    <Text fontSize="sm" color="gray.600">
                      {chunk.features.acoustic.zcr.toFixed(4)}
                    </Text>
                  </Box>
                  
                  {/* Spectral Features */}
                  <Box mb={3}>
                    <Text fontWeight="bold">Spectral Features:</Text>
                    <Text fontSize="sm" color="gray.600">
                      Centroid: {chunk.features.acoustic.spectral.centroid.toFixed(2)} Hz<br />
                      Bandwidth: {chunk.features.acoustic.spectral.bandwidth.toFixed(2)} Hz<br />
                      Flux: {chunk.features.acoustic.spectral.flux.toFixed(4)}<br />
                      Roll-off: {chunk.features.acoustic.spectral.rolloff.toFixed(2)} Hz
                    </Text>
                  </Box>
                  
                  {/* Voice Onset Time */}
                  {chunk.features.acoustic.vot !== null && (
                    <Box mb={3}>
                      <Text fontWeight="bold">Voice Onset Time:</Text>
                      <Text fontSize="sm" color="gray.600">
                        {chunk.features.acoustic.vot.toFixed(4)} seconds
                      </Text>
                    </Box>
                  )}
                </SimpleGrid>
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