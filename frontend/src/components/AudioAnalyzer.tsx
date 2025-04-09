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
  useColorModeValue,
  Container,
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
      <Box 
        as="header" 
        w="100%" 
        borderBottom="1px" 
        borderColor={useColorModeValue('gray.200', 'gray.700')}
        bg={useColorModeValue('white', 'black')}
        position="fixed"
        top={0}
        zIndex={10}
        px={8}
        py={6}
        shadow="sm"
      >
        <Container maxW="container.xl">
          <Heading 
            size="xl" 
            color={useColorModeValue('black', 'white')}
            fontWeight="bold"
            letterSpacing="tight"
          >
            Psychometric Audio Analysis
          </Heading>
          <Text 
            fontSize="md" 
            color={useColorModeValue('gray.600', 'gray.400')}
            mt={2}
          >
            Upload an audio file to analyze its features in real-time
          </Text>
        </Container>
      </Box>

      {/* Add spacing to account for fixed header */}
      <Box h="160px" />

      <Container maxW="container.xl">
        <Grid templateColumns="repeat(12, 1fr)" gap={8}>
          {/* Left Column - Main Analysis Flow */}
          <GridItem colSpan={7}>
            <VStack spacing={8}>
              <Box 
                bg={useColorModeValue('white', 'black')} 
                p={8} 
                borderRadius="xl" 
                shadow="lg" 
                border="1px solid"
                borderColor={useColorModeValue('gray.100', 'gray.800')}
                w="100%"
              >
                <VStack spacing={4} align="stretch" w="100%">
                  <FileUploader onFileSelect={handleFileSelect} />
                  
                  {file && (
                    <>
                      <Box 
                        p={4} 
                        bg={useColorModeValue('gray.50', 'gray.900')}
                        borderRadius="md"
                        border="1px dashed"
                        borderColor={useColorModeValue('gray.200', 'gray.700')}
                      >
                        <Text fontWeight="medium" color={useColorModeValue('gray.700', 'gray.300')}>
                          Selected File: {file.name}
                        </Text>
                      </Box>
                      
                      <Box>
                        <AudioVisualizer
                          file={file}
                          results={results}
                          progress={progress}
                        />
                      </Box>
                    </>
                  )}
                </VStack>
              </Box>

              <Box 
                bg={useColorModeValue('white', 'black')} 
                p={8} 
                borderRadius="xl" 
                shadow="lg"
                border="1px solid"
                borderColor={useColorModeValue('gray.100', 'gray.800')}
                w="100%"
              >
                <FeatureSelector
                  selectedFeatures={selectedFeatures}
                  onFeaturesChange={setSelectedFeatures}
                  onAnalyze={handleAnalyze}
                  isAnalyzing={progress > 0 && progress < 100}
                />
              </Box>
            </VStack>
          </GridItem>

          {/* Right Column - Results */}
          <GridItem colSpan={5} position="relative">
            {results && (
              <Box 
                bg={useColorModeValue('white', 'black')} 
                p={8} 
                borderRadius="xl" 
                shadow="lg"
                border="1px solid"
                borderColor={useColorModeValue('gray.100', 'gray.800')}
                position="sticky"
                top="180px"
              >
                <Progress
                  value={progress}
                  size="md"
                  colorScheme="green"
                  mb={6}
                  borderRadius="full"
                  hasStripe={progress < 100}
                  isAnimated={progress < 100}
                  bg={useColorModeValue('gray.100', 'gray.700')}
                />
                <AnalysisResults results={results} />
              </Box>
            )}
          </GridItem>
        </Grid>
      </Container>
    </VStack>
  )
} 