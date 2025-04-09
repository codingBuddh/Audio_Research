import { useState, useCallback, useEffect } from 'react'
import {
  Box,
  VStack,
  Heading,
  Text,
  useToast,
  Progress,
  Grid,
  GridItem,
} from '@chakra-ui/react'
import { FileUploader } from './FileUploader'
import { FeatureSelector } from './FeatureSelector'
import { AudioVisualizer } from './AudioVisualizer'
import { AnalysisResults } from './AnalysisResults'
import { AudioFeatureType, ChunkStatus } from '../types'
import { analyzeAudio, connectToWebSocket } from '../api'

export const AudioAnalyzer = () => {
  const [file, setFile] = useState<File | null>(null)
  const [selectedFeatures, setSelectedFeatures] = useState<AudioFeatureType[]>([])
  const [taskId, setTaskId] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState<any>(null)
  const toast = useToast()

  const handleFileSelect = useCallback((file: File) => {
    setFile(file)
  }, [])

  const handleAnalyze = async () => {
    if (!file || selectedFeatures.length === 0) {
      toast({
        title: 'Error',
        description: 'Please select a file and at least one feature type',
        status: 'error',
      })
      return
    }

    try {
      console.log('Starting analysis with features:', selectedFeatures)
      const response = await analyzeAudio(file, selectedFeatures)
      console.log('Analysis response:', response)
      setTaskId(response.task_id)
      setResults(response)
    } catch (error) {
      console.error('Analysis error:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to start analysis',
        status: 'error',
      })
    }
  }

  useEffect(() => {
    if (taskId) {
      const ws = connectToWebSocket(taskId)
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        setResults(data)
        
        // Calculate progress
        const completed = data.chunks.filter(
          (chunk: any) => chunk.status === ChunkStatus.COMPLETED
        ).length
        setProgress((completed / data.total_chunks) * 100)
      }

      return () => {
        ws.close()
      }
    }
  }, [taskId])

  return (
    <VStack spacing={8} align="stretch">
      <Box textAlign="center">
        <Heading size="2xl" mb={2} color="brand.600">
          Audio Analysis Dashboard
        </Heading>
        <Text fontSize="lg" color="gray.600">
          Upload an audio file to analyze its features in real-time
        </Text>
      </Box>

      <Grid templateColumns="repeat(12, 1fr)" gap={6}>
        <GridItem colSpan={[12, 12, 8]}>
          <Box bg="white" p={6} borderRadius="lg" shadow="base">
            <FileUploader onFileSelect={handleFileSelect} />
            {file && (
              <AudioVisualizer
                file={file}
                results={results}
                progress={progress}
              />
            )}
          </Box>
        </GridItem>

        <GridItem colSpan={[12, 12, 4]}>
          <VStack spacing={6}>
            <Box bg="white" p={6} borderRadius="lg" shadow="base" w="full">
              <FeatureSelector
                selectedFeatures={selectedFeatures}
                onFeaturesChange={setSelectedFeatures}
                onAnalyze={handleAnalyze}
                isAnalyzing={progress > 0 && progress < 100}
              />
            </Box>

            {results && (
              <Box bg="white" p={6} borderRadius="lg" shadow="base" w="full">
                <Progress
                  value={progress}
                  size="sm"
                  colorScheme="brand"
                  mb={4}
                />
                <AnalysisResults results={results} />
              </Box>
            )}
          </VStack>
        </GridItem>
      </Grid>
    </VStack>
  )
} 