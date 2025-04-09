import { ChakraProvider, Box, Container } from '@chakra-ui/react'
import { AudioAnalyzer } from './components/AudioAnalyzer'
import { theme } from './theme'

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Box minH="100vh" bg="gray.50">
        <Container maxW="container.xl" py={8}>
          <AudioAnalyzer />
        </Container>
      </Box>
    </ChakraProvider>
  )
}

export default App
