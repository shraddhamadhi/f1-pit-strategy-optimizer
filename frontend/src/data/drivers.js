import kimiImg from '../assets/kimi.png'
import georgeImg from '../assets/george.png'
import landoImg from '../assets/lando.png'
import oscarImg from '../assets/oscar.png'
import charlesImg from '../assets/charles.png'
import lewisImg from '../assets/lewis.png'

export const drivers = [
  // Mercedes
  { name: 'George Russell', number: 63, team: 'Mercedes', nationality: 'United Kingdom', color: '#2AD7BB', image: georgeImg, total: 159, podiums: 27, wins: 11, wdcs: 0, top: '50%', left: '30%', rotate: 1 },
  { name: 'Kimi Antonelli', number: 12, team: 'Mercedes', nationality: 'Italy', color: '#2AD7BB', image: kimiImg, total: 31, podiums: 9, wins: 5, wdcs: 0, top: '20%', left: '60%', rotate: -5 },

  // McLaren
  { name: 'Lando Norris', number: 1, team: 'McLaren', nationality: 'United Kingdom', color: '#FF8000', image: landoImg, total: 158, podiums: 46, wins: 11, wdcs: 1, top: '5%', left: '10%' },
  { name: 'Oscar Piastri', number: 81, team: 'McLaren', nationality: 'Australia', color: '#FF8000', image: oscarImg, total: 75, podiums: 28, wins: 9, wdcs: 0, top: '5%', left: '40%' },

  // Ferrari
  { name: 'Charles Leclerc', number: 16, team: 'Ferrari', nationality: 'Monaco', color: '#E80020', image: charlesImg, total: 178, podiums: 52, wins: 27, wdcs: 0, top: '50%', left: '10%' },
  { name: 'Lewis Hamilton', number: 44, team: 'Ferrari', nationality: 'United Kingdom', color: '#E80020', image: lewisImg, total: 387, podiums: 206, wins: 106, wdcs: 7, top: '70%', left: '60%' },
]